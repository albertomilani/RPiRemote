# RPiRemote

Remote ZWO ASI120MM controller on Raspberry Pi.

Use three Raspberry Pi to stream image from three ZWO ccds to a single client.

## Prerequisites
* Python-zwoasi required - https://github.com/stevemarple/python-zwoasi
* ZWO SDK

## How to use
### Raspberry side
The ZWO SDK is expected to be in
```
/opt/ASI_SDK/lib/armv7/libASICamera2.so
```

Copy the server files:
```
sudo cp asi_server.py /usr/local/bin/asi_server.py
sudo cp asi_server.service /lib/systemd/system/asi_server.service
```

then enable and start the service:
```
sudo systemctl enable asi_server.service
sudo systemctl start asi_server.service
```

### Client side
Edit cerbero.py to specify the ip addresses of the three Raspberry Pi, then launch:
```
./cerbero.py
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details 

