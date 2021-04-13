#!/bin/bash

manufacturer="Nintendo"
product="Switch(Lakka)"
#vid/pid defaults if not ran as attackmode.... Defaults are default for linux
vid_default="0x057e" #Nintendo
pid_default="0x2001" #Switch pid+1
serialnumber="00000000"

gadget_config="/sys/kernel/config"
udc="700d0000.xudc"

create_gadget_framework() {
	#create basic gadget framework to work with
        mkdir -p $gadget_config
        mount -t configfs none $gadget_config
	mkdir -p $gadget_config/usb_gadget/g
	chmod -R 666 $gadget_config/usb_gadget/g
	echo $vid_default > $gadget_config/usb_gadget/g/idVendor  
	echo $pid_default > $gadget_config/usb_gadget/g/idProduct
	echo 0x0100 > $gadget_config/usb_gadget/g/bcdDevice # v1.0.0
	echo 0x0200 > $gadget_config/usb_gadget/g/bcdUSB    # USB 2.0
	mkdir -p $gadget_config/usb_gadget/g/strings/0x409
	echo $serialnumber > $gadget_config/usb_gadget/g/strings/0x409/serialnumber
	echo $manufacturer > $gadget_config/usb_gadget/g/strings/0x409/manufacturer
	echo $product  > $gadget_config/usb_gadget/g/strings/0x409/product
 	echo 0xEF > $gadget_config/usb_gadget/g/bDeviceClass
	echo 0x02 > $gadget_config/usb_gadget/g/bDeviceSubClass
	echo 0x01 > $gadget_config/usb_gadget/g/bDeviceProtocol
	mkdir -p $gadget_config/usb_gadget/g/configs/c.1
	echo 250 > $gadget_config/usb_gadget/g/configs/c.1/MaxPower	
}

create_serial() {
	mkdir -p $gadget_config/usb_gadget/g/functions/acm.usb0
	ln -s $gadget_config/usb_gadget/g/functions/acm.usb0 $gadget_config/usb_gadget/g/configs/c.1/
}

finalize_gadget_framework() {
	echo $udc > $gadget_config/usb_gadget/g/UDC
	udevadm settle -t 5 || :
}

create_gadget_framework
create_serial
finalize_gadget_framework
