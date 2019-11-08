import os
import sys
import json
import yaml
import socket
import http.client


def parse_yml(yml_file="itm6-integrity-check.yml"):
    """Return the parsed yaml configuration file requered by the script <pc>.

    Keyword arguments:
    yml_file -- file to parse (default: conf/conf.yml)
    """
    try:
        with open(yml_file, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                sys.exit(14)
    except:
        print("Unable to open config file")
        sys.exit(10)


def tacmd_pc(pc, tgrep=False):
    """return a list with the agents = y for tacmd -y <pc>.

    Keyword arguments:
    pc -- product code (ex: UD, NT, LZ)
    tgrep -- special grep used from yml file (defaul: False)
    """
    if tgrep:
        cmd = "tacmd listsystems -t {} | grep -w Y | {}".format(pc, tgrep)
    else:
        cmd = "tacmd listsystems -t {} | grep -w Y".format(pc)

    onlineAgents = os.popen(cmd).read().strip()
    agents = [ag.split()[0] for ag in onlineAgents.split("\n")]
    return agents


def get_ITMREST(cfg, agent, ibmStatic, MetricGroup):
    """return the json from ITMRest.

    Keyword arguments:
    cfg -- cfg called from parse_yml function
    ibmStatic -- %25IBM.STATICXXX
    MetricGroup -- MetricGroup.XXXXX
    """

    tep = cfg["tep"]
    hub = cfg["hub"]
    restp = cfg["restp"]

    conn = http.client.HTTPConnection(tep, port=15200, timeout=5)
    url = ("/ibm/tivoli/rest/providers/itm.HUB_{}"
           "/datasources/TMSAgent.%25IBM.{}"
           "/datasets/MetricGroup.{}"
           "/items?&param_SourceToken={}"
           "&properties=all".format(hub, ibmStatic, MetricGroup, agent)
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


def call_report(cfg, agents, ibmStatic, MetricGroup):
    """pre report processing.

    Keyword arguments:
    cfg -- cfg called from parse_yml function
    agents -- output from tacmd_pc
    ibmStatic --  ibmStaticXXX
    MetricGroup -- MetricGroup.XXXXX
    """

    for ag in agents:
        # if any metric is already broken
        # no need to continue, it is already an issue
        agerr = False
        for m in MetricGroup:
            if agerr:
                break
            json_obj = get_ITMREST(cfg, ag, ibmStatic, m)

            if json_obj == "timeout":
                agerr = True
                print("{};{};timeout".format(ag, m))
            else:
                try:
                    lenobj = len(json_obj['items'])
                    if lenobj <= 0:
                        print("{};{};problem".format(ag, m))
                        agerr = True
                except KeyError:
                    print("{};{};unknowError".format(ag, m))
                    agerr = True
                # else:
                #     print("{};{};OK".format(ag, m))


def main():
    # parse yml
    cfg = parse_yml()
    pc = cfg["pc"]

    print("Agent;MetricGroup;Status")

    for p in pc:
        try:
            tgrep = pc[p]['tgrep']
        except KeyError:
            tgrep = False
        agents = tacmd_pc(p, tgrep)
        ibmStatic = pc[p]["ibmStatic"]
        MetricGroup = pc[p]["MetricGroup"]
        call_report(cfg, agents, ibmStatic, MetricGroup)


if __name__ == "__main__":
    main()
