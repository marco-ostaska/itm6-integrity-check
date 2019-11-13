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
restp: "abcdferfgtre=="             # b64 user and passord for ITMRest

slack:
  channel: '#channel-name'          # slack channel to receive the msg
  user: "slack-user-to-alert"       # the user you want to alert
  emoji: ':slack:'                  # slack emoji to use
  token: 'XXXXXXX/YYYYYY/ZZZZZ'     # slack webhook token

pc:
  SA:                               # ITM product Code (in this case SA)
    check: True                     # Boolean flag to mark if it should be processed or not (optional, defaults to False)
    ibmStatic: "STATIC049"          # ITMREST id referent to product code
    MetricGroup:                    # list of metric groups to collect from
      - "KSAALERTS" # Alerts
      - "KSASLOG"   # System Log
      - "KSABUFFER" # Buffer Performance (Superseded)
      - "KSASYS"    # Instance Configuration
      - "KSALOCKS"  # Lock Entries
      - "KSADUMPS"  # ABAP Dumps
      - "KSAPROCESS" # Work Processes
    tgrep: "grep -i :Ins"           # used for tacmd in case of -t <pc> is not enough

```

### TESTED PRODUCT CODES

```yml
pc:
  LZ:
    ibmStatic: "STATIC134"
    MetricGroup:
      - "LNXSYS"        # Linux System Static
      - "KLZCPU"        # Linux CPU
  IS:
    ibmStatic: "STATIC126"
    MetricGroup:
      - "KISTCPPORT"    # KIS TCPPORT
      - "KISMSTATS"     # KIS MONITOR STATUS
      - "KISHTTP"       # KIS HTTP
  OQ:
    ibmStatic: "STATIC067"
    MetricGroup:
      - "KOQDBS"
      - "KOQPROBS"
  S7:
    ibmStatic: "SAP_HANA"
    MetricGroup:
      - "KS7CURALRT"    # KS7 CURRENT ALERTS
      - "KS7SYSDB"      # KS7 SYSTEM DATABASE
      - "KS7HOSTINF"    # KS7 HOST INFORMATION
    tgrep: "grep -i :S7"
  NT:
    ibmStatic: "STATIC021"
    MetricGroup:
      - "WTSYSTEM"      # System
      - "NTSERVICE"     # Services
  UD:
    ibmStatic: "STATIC121"
    MetricGroup:
      - "KUD4238000"
      - "KUDTABSPC"
      - "KUD3437600"
  UX:
    ibmStatic: "STATIC013"
    MetricGroup:
      - "KUXPASMGMT"
      - "UNIXDCSTAT"
  SA:
    ibmStatic: "STATIC049"
    MetricGroup:
      - "KSAALERTS"     # Alerts
      - "KSASLOG"       # System Log
      - "KSABUFFER"     # Buffer Performance (Superseded)
      - "KSASYS"        # Instance Configuration
      - "KSALOCKS"      # Lock Entries
      - "KSADUMPS"      # ABAP Dumps
      - "KSAPROCESS"    # Work Processes
    tgrep: "grep -i :Ins"
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
