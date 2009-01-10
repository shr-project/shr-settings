PREFIX="/usr/local"

all: build

build:
	#it is python ;)
	exit 0

clean:
	rm -f *.pyc *~ *.pyo \
	shr_settings_modules/*.pyc shr_settings_modules/*~ shr_settings_modules/*.pyo

install:
	mkdir -p ${prefix}/
	install -m 0644 data/shr_settings.png ${PREFIX}/share/pixmaps
	install -m 0644 data/shr-settings.desktop ${PREFIX}/share/applications
	install -m 0755 shr-settings ${PREFIX}/bin
	mkdir -p ${PREFIX}/lib/python2.5/site-packages/shr_settings_modules
	install -m 0644 shr_settings_modules/*.py ${PREFIX}/lib/python2.5/site-packages/shr_settings_modules
