#!/bin/bash

export TEXTDOMAIN="tuquito-adsl"
export TEXTDOMAINDIR="/usr/share/tuquito/locale"
FRONTEND="zenity"
CAPTION=$(gettext "Configuring ADSL modem")

zona(){
	$FRONTEND --title "$CAPTION" --list --text=$(gettext "Which zone do you belong?") --column=$(gettext "Zone")  "Arnet" "Speedy" > /tmp/configsave

	if [ $? = 0 ]; then

		modprobe ueagle-atm 2> /dev/null

		SAVE=`cat /tmp/configsave | tr -d '"'`

		if [ "$SAVE" = "Arnet" ]; then
			`modprobe br2684 && br2684ctl -c 0 -b -a 0.33 && ifconfig nas0 up`
		elif [ "$SAVE" = "Speedy" ]; then
			`modprobe br2684 && br2684ctl -c 0 -b -a 8.35 && ifconfig nas0 up`
		fi

		$FRONTEND --title "$CAPTION" --question --text=$(gettext "Do you want to automatically load your modem at the beginning of Tuquito?")

		if [ $? = 0 ]; then
			test  -L /etc/rc2.d/S99amigo &&  rm /etc/rc2.d/S99amigo
			test -f /etc/init.d/amigo-tuquito && rm -f /etc/init.d/amigo-tuquito

			if [ $SAVE = "Arnet" ]; then
				cp /usr/share/tuquito/adsl/amigo-tuquito-arnet /etc/init.d/amigo-tuquito
			elif [ $SAVE = "Speedy" ]; then
				cp /usr/share/tuquito/adsl/amigo-tuquito-speedy /etc/init.d/amigo-tuquito
			fi

			ln -s /etc/init.d/amigo-tuquito /etc/rc2.d/S99amigo
		fi
	else
		exit 1
	fi
}

amigo(){
	$FRONTEND --title="$CAPTION" --info --text=$(gettext "Wait until the link LED of your modem, is fully on and press OK to continue (Aprox. 40 seconds).")
	if [ $? = 0 ]; then
		zona && $FRONTEND --title="$CAPTION" --info --text=$(gettext "The modem was configured successfully"); exit 0
	else
		exit 1
	fi
}

USB(){
	$FRONTEND --title "$CAPTION" --list --text=$(gettext "What driver is compatible with your modem?") --column=$(gettext "Drivers")  "Amigo/Zyxel" "Eagle" "SpeedTouch" > /tmp/configsave
	if [ $? = 0 ]; then
		amigo
	else
		exit 1
	fi
}

Ethernet(){
 `nm-connection-editor`
}

main(){
	$FRONTEND --title "$CAPTION" --list --text=$(gettext "What type of modem you have?") --column=$(gettext "Types")  "USB" "Ethernet" > /tmp/configsave
	if [ $? = 0 ]; then
		`cat /tmp/configsave`
	else
		exit 1
	fi
}

main
