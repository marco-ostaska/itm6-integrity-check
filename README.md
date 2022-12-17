# ITM6 Integrity Check

The ITM6 Integrity Check is a script that helps you ensure the integrity of your ITM6 agents by checking their data collection status via ITMRest. By connecting to ITMRest and querying the status of specific metrics, the script can help you verify that your agents are functioning correctly and providing the expected data.

### SYNOPSIS

```shell
python itm6-integrity-check.py <config-file>
```

### DESCRIPTION

The itm6-integrity-check.py script connects to ITMRest using the credentials and configuration provided in a YAML configuration file. It then checks the status of specific metrics for each of the specified product codes, as defined in the configuration file. If any issues are found, the script will report them and provide details about the problem.

The script uses the ITM product codes and metric groups specified in the configuration file to determine which metrics to check. You can customize the script by adding or removing product codes and metric groups as needed.

### ENVIRONMENT

In order to run the itm6-integrity-check.py script, you will need the following:

- ITMRest enabled on your system
- Python 3.4 or higher, along with the json and pyyaml modules

## CONFIGURATION

All configuration for the script is done through the itm6-integrity-check.yml file, which should be placed in the same directory as the script. Alternatively, you can specify the path to the configuration file as a command line argument when running the script.

Here is an example of the structure and format of the YAML configuration file:

```yaml
tep: "tepserver1"                   # your tep name
hub: "htem1"                        # your htem name
restp: "abcdefghijkl=="             # b64 user and passord for ITMRest
cycle:                              # timw to wait in sec before check for next pc

slack:
  channel: '#channel-name'          # slack channel to receive the msg
  user: "slack-user-to-alert"       # the user you want to alert
  emoji: ':slack:'                  # slack emoji to use
  token: 'XXXXXXX/YYYYYY/ZZZZZ'     # slack webhook token

pc:
  LZ:                               # ITM product Code (in this case LZ)
    check: True                     # Boolean flag to mark if it should be processed or not (optional, defaults to False)
    ibmStatic: "STATIC049"          # ITMREST id referent to product code
    MetricGroup:                    # list of metric groups to collect from
      LNXSYS:                         # Linux System Static
        SYSUPTIM                        # System Uptime
      KLZCPU:                         # Linux CPU
        SYSCPU                          # System CPU (Percent)
    tgrep: "grep -i :LZ"             # used for tacmd in case of -t <pc> is not enough

```

### TESTED PRODUCT CODES

Here are some examples of the product codes and metric groups that are supported by the script:

```yml
pc:
  LZ:
    check: true
    ibmStatic: "STATIC134"
    MetricGroup:
      LNXSYS:                 # Linux System Static
        SYSUPTIM                # System Uptime
      KLZCPU:                 # Linux CPU
        SYSCPU                  # System CPU (Percent)
  SA:
    check: True
    ibmStatic: "STATIC049"
    MetricGroup:
      KSASYS:                 # Instance Configuration
        "INSTANCE,INST_NO"       # Instance Name, Instance Number
    tgrep: "grep -i :Ins"
  S7:
    check: True
    ibmStatic: "SAP_HANA"
    MetricGroup:
      KS7SYSDB:              # KS7 SYSTEM DATABASE
        STATUS                 # DB Status
      KS7HOSTINF:           # KS7 HOST INFORMATION
        STATUS                 # Status
    tgrep: "grep -i :S7"
  RZ:
    check: True
    ibmStatic: "OracleAgentRDB"
    MetricGroup:
      KRZACTINS:            # KRZ RDB ACTIVE INSTANCE
        "INSTNAME, STATUS"    # "Instance Name, STATUS"
    tgrep: "grep -E '^RZ'"
  3Z:
    check: True
    ibmStatic: STATIC168
    MetricGroup:
      K3ZNTDSDCA:            # Domain Controller Availability
        DCARPP                 # DCA Repl Partners
  OQ:
    check: True
    ibmStatic: STATIC067
    MetricGroup:
      KOQDBD:               # MS SQL Database Detail
        DBNAME                # Database Name
      KOQJOBD:              # MS SQL Job Detail
        KOQJOBD              # Job Id
  UX:
    check: True
    ibmStatic: STATIC013
    MetricGroup:
      UNIXOS:              # System
        SYSTEMTYPE           # Type
  Q5:
    check: True
    ibmStatic: STATIC107
    MetricGroup:
      KQ5AVAIL:          # KQ5 AVAILABILITY
        STATUS             # Status
  IS:
    check: True
    ibmStatic: STATIC126
    MetricGroup:
      KISSISTATS:       # KIS SERVICE INSTANCE STATISTICS
        ISMPROFILE        #  Profile
  LO:
    check: True
    ibmStatic: KLO
    MetricGroup:
      KLOLOGFST:       # KLO LOG FILE STATUS
        FILSTAT          # File Status
    tgrep: "grep :LO"
  NT:
    check: True
    ibmStatic: STATIC021
    MetricGroup:
      NTCOMPINFO:      # Computer Information
        COMPFQDN         # Computer Domain Name
```

### OUTPUT

The script will output a message for each product code that is checked. If the agents for the product code are collecting data correctly, the message will contain a list of the agents that are online. If there is an error, the message will contain information about the error and the agents that were affected.

If the slack configuration option is set in the YAML file, the script will also send messages to the specified Slack channel. The messages will contain the same information as the output to the console.

### TROUBLESHOOTING
If you encounter any errors or issues while running the script, check the following:

- Make sure that ITMRest is enabled and that you have a valid username and password for accessing it.
- Check the configuration file for any errors or typos.
- If you are having trouble connecting to ITMRest, try running the tacmd command tacmd login to verify that you can authenticate with the server.
- If you are seeing errors related to metric groups or metrics, make sure that the names are spelled correctly and that they exist on your system.
- If you are having trouble connecting to Slack, verify that the webhook token is correct and that you have permission to post to the specified channel.

### EXIT CODES

There some different error codes and their corresponding error messages that may appear during bad conditions. At the time  of  this  writing,  the exit codes are:

```
10    Missing argument <yml file>
11    yaml.YAMLError (unable to parse yaml file)
12    Unable to open config file, please check permission
13    Unable to open config file, file not found
14    Failed to connect to API
```


### SEE ALSO

- [ITMRest documentation](https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_7.6.0/com.ibm.tm.itm.doc/itm_rest_reference.html)
- [Slack API documentation](https://api.slack.com/)
