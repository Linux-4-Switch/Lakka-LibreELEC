#!/bin/bash

gadget_config="/sys/kernel/config"
#Manufacturer and Product the device reports to OS. Doesnt really matter what you put here.
manufacturer="Who Ever Owns This"
product="Pure Awesomeness"
#vid/pid defaults if not ran as attackmode.... Defaults are default for linux
vid_default="0x1d6b" #linux foundation
pid_default="0x0104" #Multifunction Gadget

udc="700d0000.xudc"

create_gadget_framework() {
	#create basic gadget framework to work with
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

create_rndis() {
	echo 1 > $gadget_config/usb_gadget/g/os_desc/use
	echo 0xcd > $gadget_config/usb_gadget/g/os_desc/b_vendor_code
	echo MSFT100 > $gadget_config/usb_gadget/g/os_desc/qw_sign
	mkdir -p $gadget_config/usb_gadget/g/functions/rndis.usb0
	echo RNDIS   > $gadget_config/usb_gadget/g/functions/rndis.usb0/os_desc/interface.rndis/compatible_id
	echo 5162001 > $gadget_config/usb_gadget/g/functions/rndis.usb0/os_desc/interface.rndis/sub_compatible_id
	[[ "x$dev_addr" != "x" ]] && echo $dev_addr > $gadget_config/usb_gadget/g/functions/rndis.usb0/dev_addr 
	[[ "x$host_addr" != "x" ]] && echo $host_addr > $gadget_config/usb_gadget/g/functions/rndis.usb0/host_addr
	ln -s $gadget_config/usb_gadget/g/functions/rndis.usb0 $gadget_config/usb_gadget/g/configs/c.1/
	ln -s $gadget_config/usb_gadget/g/configs/c.1 $gadget_config/usb_gadget/g/os_desc
}

finalize_gadget_framework() {
	echo $udc > $gadget_config/usb_gadget/g/UDC
	udevadm settle -t 5 || :
}

create_gadget_framework
create_rndis
finalize_gadget_framework

ifconfig usb0 172.16.64.1 netmask 255.255.255.0; ifconfig usb0 up
