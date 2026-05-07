#!/bin/bash

# Shell Script to Run the ROS roscore executable.

# Likely ROS environment settings as an example:
#ROS_ETC_DIR=/opt/ros/indigo/etc/ros
#ROS_MASTER_URI=http://localhost:11311

SETUP_FILE="setup.bash"
ROSCORE_HOST=
ROSCORE_PORT=

set_roscore_host()
{
    ROSCORE_HOST=`echo "$ROS_MASTER_URI" | sed -e 's/http:\/\///g' | sed -e 's/:[0-9]*//g'`
}

set_roscore_port()
{
    ROSCORE_PORT=`echo "$ROS_MASTER_URI" | sed -e 's/http:\/\///g' | sed -e 's/.*:\([0-9]*\)/\1/g'`
}

show_roscore_host()
{
    set_roscore_host
    echo -n "$ROSCORE_HOST"
}

show_roscore_port()
{
    set_roscore_port
    echo -n "$ROSCORE_PORT"
}

show_roscore_host_port()
{
    echo -n "roscore host: "
    show_roscore_host
    echo
    echo -n "roscore port: "
    show_roscore_port
}

is_roscore_running()
{
    roscore_host=$1
    roscore_port=$2
    roscore_http_conn_resp=`nc -z -v $roscore_host $roscore_port 2>&1 | grep "^Connection.*succeeded!"`

    if [ ! "$roscore_http_conn_resp" = "" ]; then
      return 1
    fi
    return 0
}

show_quick_help()
{
    echo "Usage:"
    echo "$ run_ros.sh"
    echo
    echo "For help, specify the -? or -h option:"
    echo "$ run_ros.h -?"
    echo "$ run_ros.sh -h"
    echo
    echo "For more extensive help, specify the --help option:"
    echo "$ run_ros.sh --help"
    echo
    echo "To check if roscore is already running, specify the -i or --is-running option."
    echo "$ run_ros.sh -i"
    echo "$ run_ros.sh --is-running"
    echo
    echo "To show the current ROS environment variables, specify the -e or --env option."
    echo "$ run_ros.sh -e"
    echo "$ run_ros.sh --env"
    echo
    echo "To source setup script files in current subdirectories, specify the -s or --source-setup option."
    echo "$ run_ros.sh -s"
    echo "$ run_ros.sh --source-setup"
    echo
    echo "To show the host and port roscore is listening on, specify the --show-host-port option."
    echo "$ run_ros.sh --show-host-port"
}

show_env()
{
    echo "Current ROS Environment Variables:"
    echo
    env|grep "ROS[A-Z,a-z,0-9,_]*"
}

show_error()
{
    if [ ! "$1" = "" ]; then
      echo "Error: $1"
      echo "Specify --help option for help."
    fi
}

show_usage()
{
    echo
    echo "Shell Script to Run the ROS roscore executable"
    echo
    show_quick_help
    echo
    show_env
    echo
    echo "Environment setup ..."
    echo "It's convenient if the ROS environment variables are automatically added to your bash session every time a new shell is launched:"
    echo
    echo "  source /opt/ros/indigo/setup.bash >> ~/.bashrc"
    echo "  source ~/.bashrc"
    echo
    echo "If you have more than one ROS distribution installed, ~/.bashrc must only source the setup.bash for the version you are currently using."
    echo "If you just want to change the environment of your current shell, you can type:"
    echo
    echo "  source /opt/ros/indigo/setup.bash"
    echo
    echo "If you use zsh instead of bash you need to run the following commands to set up your shell:"
    echo
    echo "  source /opt/ros/indigo/setup.zsh"
    echo
    echo "Run ROS Core executable..."
    echo
    echo "  roscore"
    echo
    echo " Note: The roscore executable might be run by another script in a project, so don't run roscore if roscore is run from another script."
    echo
}

# run roscore executable
run()
{
    roscore
}

# source setup files in subdirectories
source_setup()
{
  SETUP_FILES=`find . -name "devel"`
  while read -r line ; do
    echo "Sourcing: $line/$SETUP_FILE"
    . $line/$SETUP_FILE
  done <<< "$SETUP_FILES"
}

# check for command-line parameters
for x in $*; do
  if [ "$x" = "-h" ] || [ "$x" = "-?" ]; then
    show_quick_help
    exit
  fi
  if [ "$x" = "--help" ] || [ "$x" = "-h" ] || [ "$x" = "-?" ]; then
    show_usage
    exit
  fi
  if [ "$x" = "--is-running" ] || [ "$x" = "-i" ]; then
      is_roscore_running "$ROSCORE_HOST" "$ROSCORE_PORT"
      if [ $? -eq 1 ]; then
      echo "roscore is running"
    else
      echo "roscore is not running."
    fi
    exit
  fi
  if [ "$x" = "-e" ] || [ "$x" = "--env" ]; then
    echo
    show_env
    echo
    exit
  fi
  if [ "$x" = "-s" ] || [ "$x" = "--source-setup" ]; then
    echo
    source_setup
    echo
    exit
  fi
  if [ "$x" = "--show-host-port" ]; then
    show_roscore_host_port
    echo
    exit
  fi
  echo "Unknown option $x"
  echo "Specify -h option for help."
  exit
done

WHICH_ROSCORE=`which roscore`
if [ "$WHICH_ROSCORE" = "" ]; then
  show_error "Error: ROSCORE does not exist."
  exit 1
fi

if [ ! -d $ROS_ETC_DIR ]; then
  show_error "Error: ROS_etc_dir does not exist: $ROS_ETC_DIR" 
  exit 2
fi

if [ "$ROS_MASTER_URI" = "" ]; then
  show_error "ROS Master URI not specified (ROS_MASTER_URI=\"$ROS_MASTER_URI\")"
  exit 3
fi

set_roscore_host "$ROS_MASTER_URI"
set_roscore_port "$ROS_MASTER_URI"

is_roscore_running "$ROSCORE_HOST" "$ROSCORE_PORT"
if [ $? -eq 1 ]; then
  echo "roscore is already running."
  exit 4
fi

show_roscore_host_port
echo
source_setup
echo
run
