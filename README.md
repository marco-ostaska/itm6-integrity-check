# ITM6 Integrity Check

- Checks ITM6 agents integrity via ITMRest

### SYNOPSIS

```shell
python itm6-integrity-check.py <config-file>
```

### DESCRIPTION

- itm6-integrity-check.py is a python script that connects via ITMRest and check if the agents is collecting data right as if you were checking on TEP.

- itm6-integrity-check.py uses specific metric provided in a yaml format, so you can added or remove MetricGroup as needed.

### ENVIRONMENT

- itm6-integrity-check.py runs on the top of ITMRest, then it needs to be enabled

- python3.4+, as (json, pyymal) modules are also required.


### itm6-integrity-check.yml

- all configuration is done into itm6-integrity-check.yml file that needs to be placed in to the same directory as the script. Other wise you need to specify one as argument

#### itm6-integrity-check.yml (example)

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


### EXIT CODES

There spme different error codes and their corresponding error messages that may appear during bad conditions. At the time  of  this  writing,  the exit codes are:

```
10    Missing argument <yml file>
11    yaml.YAMLError (unable to parse yaml file)
12    Unable to open config file, please check permission
13    Unable to open config file, file not found
14    Failed to connect to API
```
