import os
import sys
import json
import base64
import yaml
import time
import socket
import http.client


class yml(object):
    """
    Class to parse ymal file
    """
    try:
        yml_file = sys.argv[1]
    except IndexError:
        print("Missing argument <yml file>")
        sys.exit(10)
    try:
        with open(yml_file, 'r') as stream:
            try:
                cfg = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                sys.exit(11)
    except PermissionError:
        print("Unable to open config file, please check permission")
        sys.exit(12)
    except FileNotFoundError:
        print("Unable to open config file, file not found")
        sys.exit(13)


class slackObj(object):
    slack = yml.cfg["slack"]
    channel = slack["channel"]
    user = "{}: {}".format(yml.cfg["hub"], slack["user"])
    emoji = slack["emoji"]
    token = slack["token"]


class PC(object):
    """
    parse product code

    Keyword arguments:
    pc -- product code (ex: UD, NT, LZ)
    """

    def __init__(self, p):
        self.tgrep = self.validate_key(p, "tgrep")
        self.check = self.validate_key(p, "check")
        self.MetricGroup = yml.cfg["pc"][p]["MetricGroup"]
        self.ibmStatic = yml.cfg["pc"][p]["ibmStatic"]
        if self.check:
            self.agents = self.tacmd_pc(p, self.tgrep)
        else:
            self.agents = False

    def validate_key(self, p, key):
        """check if key exits in parse

        Keyword arguments:
        p -- prodct code parsed from yml
        key -- key to validate
        """
        try:
            return yml.cfg["pc"][p][key]
        except KeyError:
            return False

    def tacmd_pc(self, pc, tgrep):
        """return a list with the agents = y for tacmd -y <pc>.

        Keyword arguments:
        pc -- product code (ex: UD, NT, LZ)
        tgrep -- special grep used from yml file (defaul: False)
        """
        if tgrep:
            cmd = "tacmd listsystems -t {} | grep -w Y | {}".format(pc, tgrep)
        else:
            cmd = "tacmd listsystems -t {} | grep -w Y".format(pc)
        b64 = base64.b64decode(yml.cfg["restp"]).decode("utf-8")
        tacmdU = b64.split(":")[0]
        tacmdP = b64.split(":")[1]
        tlogin = "tacmd login -s {} -u {} -p {} -t 60".format(yml.cfg["hub"], tacmdU, tacmdP)

        os.popen(tlogin).read().strip()
        onlineAgents = os.popen(cmd).read().strip()
        agents = [ag.split()[0] for ag in onlineAgents.split("\n")]
        os.popen("tacmd logout").read().strip()
        return agents


class ERRORs(object):
    def __init__(self):
        self.err_lst = []
        self.timeout_lst = []
        self.flag = False


def get_hostname(agent):
    commaSlipt = agent.split(":")
    dashPrefixed = commaSlipt[len(commaSlipt)-2].split("_")

    # if it just comma separated
    if len(dashPrefixed) == 1 and commaSlipt[0] != "RZ":
        return commaSlipt[len(commaSlipt)-2].lower()
    else:
        if commaSlipt[0] == "RZ":
            split_list = commaSlipt[1].split("-")
            s = split_list[-1] if len(split_list) <= 3 else "{}-{}".format(
                split_list[len(split_list)-2], split_list[-1])
            return s.lower()
        elif len(dashPrefixed[len(commaSlipt)-2].split("-")) == 2:
            return dashPrefixed[len(commaSlipt)-2].split("-")[1].lower()
        elif len(dashPrefixed[len(commaSlipt)-2].split("-")) >= 2:
            p1 = dashPrefixed[len(commaSlipt)-2].split("-")[1]
            p2 = dashPrefixed[len(commaSlipt)-2].split("-")[2]
            return "{}-{}".format(p1.lower(), p2.lower())


def slackme(channel, usr, msg, emoji, token):
    """send slack message to a channel.

    Keyword arguments:
    channel -- slack channel name
    usr     -- slack user name
    msg     -- message to be sent (need to be a list)
    emoji   -- slack emoji
    token   -- slack token
    """

    conn = http.client.HTTPSConnection("hooks.slack.com")

    payload = {'channel': channel,
               'username': usr,
               'text': '\n'.join(msg),
               'icon_emoji': emoji}

    jpayload = json.dumps(payload).encode()

    headers = {'Content-type': 'application/json'}

    conn.request(
        'POST',
        '/services/{}'.format(token),
        jpayload, headers)

    res = conn.getresponse()
    data = res.read()

    print("Slack message: {}".format(data.decode("utf-8")))


def get_ITMREST(agent=None, ibmStatic="Validate", MetricGroup=False, properties=None):
    """return the json from ITMRest.

    Keyword arguments:
    agent -- agent list, needed if ibmStatic != "Validate"
    ibmStatic -- %25IBM.STATICXXX or Validate (to check is API is accesible)
    MetricGroup -- MetricGroup.XXXXX required for agent check and False for ibmStatic=Validate (default: False)
    timeout -- timeout for request api (default: 10)
    """

    tep = yml.cfg["tep"]
    hub = yml.cfg["hub"]
    restp = yml.cfg["restp"]

    conn = http.client.HTTPConnection(tep, port=15200, timeout=60)
    if ibmStatic == "Validate":
        url = ("/ibm/tivoli/rest/providers/itm.HUB_{}".format(hub))
    else:
        url = ("/ibm/tivoli/rest/providers/itm.HUB_{}"
               "/datasources/TMSAgent.%25IBM.{}"
               "/datasets/MetricGroup.{}"
               "/items??optimize=true"
               "&param_SourceToken={}"
               "&properties={}"
               "&start=0&count=1&param_Limit=2".format(
                   hub, ibmStatic, MetricGroup, agent, properties)
               )

    headers = {
        'Authorization': "Basic {}".format(restp),
        'cache-control': "no-cache",
    }
    try:
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        return json.loads(data)
    except socket.timeout:
        return "timeout"
    except socket.gaierror:
        return "uriUknown"


def IntegrityCheck(pcObj):
    """return a list with agents with errors and anotother for timeout

    Keyword arguments:
    pcObj -- product code object
    retry -- if it is a retry (default 0)
    """
    errObj = ERRORs()

    for ag in pcObj.agents:
        stime = time.time()
        # if any metric is already broken
        # no need to continue, it is already an issue
        errObj.flag = False
        for m, pr in pcObj.MetricGroup.items():
            if errObj.flag:
                break
            json_obj = get_ITMREST(ag, pcObj.ibmStatic, m, pr)

            if json_obj == "timeout":
                errObj.flag = True
                errObj.timeout_lst.append([ag, m, "timeout"])
                print("{};{};timeout".format(ag, m))
                test_api()
            else:
                try:
                    lenobj = len(json_obj['items'])
                    if lenobj <= 0:
                        errObj.err_lst.append([ag, m, "notCollecting"])
                        print("{};{};notCollecting".format(ag, m))
                        errObj.flag = True
                except KeyError:
                    errObj.err_lst.append([ag, m, "Offline or removed"])
                    print("{};{};KeyError".format(ag, m))
                    errObj.flag = True
                except:
                    errObj.err_lst.append([ag, m, "unknowError"])
                    print("{};{};unknowError".format(ag, m))
                    errObj.flag = True
        etime = round(time.time() - stime)
        sleeptime = (etime * 2) if (etime * 2) > 0 else 0.5

        server = get_hostname(ag)
        print("{} - {} [{},{}]".format(server, ag, etime, sleeptime))
        time.sleep(sleeptime)
    return errObj


def test_api():
    rest_response = get_ITMREST()
    if rest_response == "timeout" or rest_response == "uriUknown":
        print("ITMREST return error: {}".format(rest_response))
        slackmsg = ["ITMREST return error: {}".format(rest_response)]
        slackme(slackObj.channel, slackObj.user,
                slackmsg, slackObj.emoji, slackObj.token)
        sys.exit(14)


def ErrReport(err, err_lst):
    slack_list = []
    print("{} {}:".format(err, len(err_lst)))
    for m in err_lst:
        server = get_hostname(m[0])
        slack_list.append("(Server:{}) {} not working properly (metricGroup: {}, errCode: {})".format(
            server, m[0], m[1], m[2]))
    print("\n".join(slack_list))
    slackme(slackObj.channel, slackObj.user,
            slack_list, slackObj.emoji, slackObj.token)


def main():
    # test api connectivity
    test_api()

    # check status for product code
    pc = yml.cfg["pc"]

    for p in pc:

        pcObj = PC(p)
        if pcObj.agents:
            errObj = IntegrityCheck(pcObj)
            if len(errObj.err_lst) > 0:
                ErrReport("ERRORS", errObj.err_lst)
            if len(errObj.timeout_lst) > 0:
                ErrReport("TIMEOUT", errObj.timeout_lst)
    time.sleep(yml.cfg["cycle"])

    # ticket


if __name__ == "__main__":
    main()
