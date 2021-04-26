#!/usr/bin/bash

function die(){
  # Display a error message and exits with error code
	echo "$1" && exit "$2"
}

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as sudo mode or root"
   exit 1
fi

# if not enough args displayed, or try to enable
# service to root then display an error and die
[ "$1" == "root" ] && die "Cannot install strino service to root" 1
[ $# -eq 0 ] && die "Usage: $0 [user]" 1

service_content="
[Unit]
Description=Strino - Share your peripherals
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=5
ExecStart=/usr/bin/env python3 $(pwd)/strino.py

[Install]
WantedBy=graphical.target
"

# We need to use "eval" bellow so we need to assert
# the value of argument $1 is a valid user
if ! id -u "$1" &>/dev/null; then
  echo "User $1 not exists"
  exit 1
fi

# Get the user home directory
user_home=$(eval echo "~$1")

# Systemd user services are located at user home
# under the path "$HOME/.config/systemd/user/"
user_service_path="${user_home}/.config/systemd/user/"

if [[ ! -d ${user_service_path} ]]; then
  echo "Creating systemd user services path"
  su - "$1" -c "mkdir -pv $user_service_path"
fi

service_name="strino.service"

# Fixme: Security fail adding normal user to root group. Normal user has no read
# Fixme: permission to /dev/input/event* and no write permission to /dev/uinput
is_in_group=0

for group in $(groups jeffersson | cut -d: -f2); do
  if [[ $group == "root" ]]; then
    is_in_group=1
  fi
done

if [[ $is_in_group -eq 0 ]]; then
  echo "Giving root access permission to user"
  usermod -a -G root "$1"
  chmod g+rw /dev/uinput
fi

if [[ ! -f "${user_service_path}/$service_name" ]]; then
  echo "Enabling strino service at boot to user: $1"
  echo "$service_content" > "${user_service_path}"/"$service_name"
  chown -R "$1":"$1" "${user_service_path}"/"$service_name"
  sudo -u "$1" XDG_RUNTIME_DIR=/run/user/"$(id -u "$1")" systemctl --user enable strino

  echo "Starting strino service right now"
  sudo -u "$1" XDG_RUNTIME_DIR=/run/user/"$(id -u "$1")" systemctl --user start strino
fi
