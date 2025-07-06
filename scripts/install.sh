#!/bin/bash

red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
blue='\033[0;34m'
purple='\033[0;35m'
cyan='\033[0;36m'
light_gray='\033[0;37m'
dark_gray='\033[1;30m'
light_red='\033[1;31m'
light_green='\033[1;32m'
light_yellow='\033[1;33m'
light_blue='\033[1;34m'
light_purple='\033[1;35m'
light_cyan='\033[1;36m'
white='\033[1;37m'
plain='\033[0m'

function LOGD() {
    echo -e "${yellow}[DEG] $* ${plain}"
}

function LOGE() {
    echo -e "${red}[ERR] $* ${plain}"
}

function LOGI() {
    echo -e "${green}[INF] $* ${plain}"
}

confirm() {
    if [[ $# > 1 ]]; then
        echo && read -p "$1 [Default $2]: " temp
        if [[ "${temp}" == "" ]]; then
            temp=$2
        fi
    else
        read -p "$1 [y/n]: " temp
    fi
    if [[ "${temp}" == "y" || "${temp}" == "Y" ]]; then
        return 0
    else
        return 1
    fi
}

SH_DIR="/usr/local/xbot"
REPO_DIR="/root/XMPLUS-TGBOT"
service="XBOT"

setup() {
    if [ -f "$SH_DIR" ] && [ $# -eq 0 ]; then
        menu
    else
        LOGI "Downloading xbot script..."
        if ! curl -fsSL -o "$SH_DIR" "https://raw.githubusercontent.com/mmdyb/XMPLUS-TGBOT/main/scripts/install.sh"; then
            LOGE "Failed to download xbot script." >&2
            exit 1
        fi
        chmod +x "$SH_DIR"

        if ! command -v unzip &> /dev/null; then
            LOGI "Installing python3-pip..."
            apt-get update && apt-get install unzip -y || exit 1
        fi

        mkdir -p "$REPO_DIR"

        DEST_DIR="XMPLUS-TGBOT-main"
        LOGI "Downloading latest repository ZIP..."
        wget -qO repo.zip "https://github.com/mmdyb/XMPLUS-TGBOT/archive/refs/heads/main.zip" || { LOGE "Failed download repository!"; exit 1; }

        LOGI "Extracting ZIP..."
        unzip -q -o repo.zip || { LOGE "Failed unzip!"; exit 1; }
        rm repo.zip
        mv "$DEST_DIR"/* "$DEST_DIR"/.* "$REPO_DIR"/ 2>/dev/null || true

        LOGI "Cleaning up old version..."
        rm -rf "$DEST_DIR"

        if ! command -v python3 &> /dev/null || ! command -v pip3 &> /dev/null; then
            LOGI "Installing python3-pip..."
            apt-get update && apt-get install python3-pip -y || exit 1
        fi

        LOGI "Installing packages..."
        pip3 install -r $REPO_DIR/requirements.txt --break-system-packages || exit 1
        before_menu
    fi
}


delete_script() {
    rm "$0"  # Remove the script file itself
    exit 1
}

uninstall() {
    confirm "Are you sure you want to uninstall (Y/N)?" "n"
    if [[ $? != 0 ]]; then
        if [[ $# == 0 ]]; then
            menu
        fi
        return 0
    fi

    service_uninstall
    rm $SH_DIR -rf

    echo ""
    echo -e "${red}Uninstalled Successfully.${plain}\n"
    hash -r
    
    trap delete_script SIGTERM
    delete_script
}

service_uninstall() {
    file="/etc/systemd/system/${service}.service"
    sudo systemctl stop $service.service
    sudo systemctl disable $service.service
    rm -rm $file
    sudo systemctl daemon-reload
    LOGE "${service}.service is removed!"
}

var() {
    local prompt_text="$1"
    local var_name="$2"
    local input

    echo -ne $prompt_text
    read input

    if [ -z "$input" ]; then
        LOGE "Input cannot be empty!"
        exit 1
    fi

    eval "$var_name=\"\$input\""
}

config() {
    clear
    var "Enter ${green}API ID${plain}: " API_ID
    var "Enter ${green}API HASH${plain}: " API_HASH
    var "Enter ${green}BOT TOKEN${plain}: " BOT_TOKEN
    var "Enter ${green}OWNER ID${plain}: " OWNER
    var "Enter ${green}PANEL URL ${white}(https://example.com)${plain}: " API_URL

    cat << EOF > "$REPO_DIR/.env"
API_ID = $API_ID
API_HASH = $API_HASH
BOT_TOKEN = $BOT_TOKEN

OWNER = $OWNER

API_URL = $API_URL
EOF
    LOGI "XBot has been successfully configured!"
    service_cli 0
    # before_menu
}

service_setup() {
    file="/etc/systemd/system/${service}.service"
    exec="/usr/bin/python3 ${REPO_DIR}/main.py"
    if [ -f $file ]; then
        return 0
    fi
    cat << EOF >> $file
[Unit]
Description=My Pyrogram Bot
After=network.target

[Service]
User=root
WorkingDirectory=${REPO_DIR}
ExecStart=${exec}
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        sudo systemctl enable $service.service
        sudo systemctl daemon-reload
        # sudo systemctl start $service.service
}

service_cli() {
    clear
    local input=$1
    if [ "$input" -eq 0 ]; then
        sudo systemctl status $service.service
    elif [ "$input" -eq 1 ]; then
        service_setup
        sudo systemctl start $service.service
        LOGI "$service.service is running..."
    elif [ "$input" -eq 2 ]; then
        LOGI "$service.service is restarting..."
        sudo systemctl restart $service.service
    elif [ "$input" -eq 3 ]; then
        LOGI "$service.service will be stopped..."
        sudo systemctl stop $service.service
    fi
    before_menu
}

before_menu() {
    echo && echo -n -e "${yellow}Press enter to return to the menu: ${plain}" && read temp
    menu
}

menu() {
    clear
    echo -e "  ${light_purple}XBOT :)${plain}\n
  ${green}[0]${plain} Exit Script\n
  ${green}[1]${plain} Update
  ${green}[2]${plain} Uninstall\n
  ${green}[3]${plain} Status
  ${green}[4]${plain} Start
  ${green}[5]${plain} Restart
  ${green}[6]${plain} Stop"

    echo && read -p "Please enter your selection: " num

    case "${num}" in
    0)
        exit 0
        ;;
    1)
        setup 1
        ;;
    2)
        uninstall
        ;;
    3)
        service_cli 0
        ;;
    4)
        service_cli 1
        ;;
    5)
        service_cli 2
        ;;
    6)
        service_cli 3
        ;;
    
    *)
        LOGE "Please enter the correct number [0-6]"
        ;;
    esac
}

setup