#! /bin/sh

PATH=${WORKSPACE}/venv/bin:$PATH

PYLINT=pylint

if [ ! -d "venv" ]; then
	virtualenv venv
fi
chmod +x ./venv/bin/activate

./venv/bin/activate
pip install --trusted-host scmesos06 -i http://scmesos06/simple -r requirements_dev.txt --cache-dir=/tmp/${JOB_NAME}
pip install --trusted-host scmesos06 -i http://scmesos06/simple Coverage --cache-dir=/tmp/${JOB_NAME}

${PYLINT} -f parseable simplekit | tee pylint.out