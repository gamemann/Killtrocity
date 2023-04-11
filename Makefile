install:
	mkdir -p /etc/killtrocity
	cp -n data/killtrocity.json /etc/killtrocity
	cp data/killtrocity.service /etc/systemd/system/killtrocity.service
	python3 -m pip install websockets