FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# FIXME : do I want to copy all I have?
COPY . .

# Updating the packages and installing cron and vim editor if you later want to edit your script from inside your container.
RUN apt-get update && apt-get install cron -y && apt-get install vim -y && apt-get install -y dos2unix

# Crontab file copied to cron.d directory. Pay attention to line ending
COPY ./cron_files/cronjob /etc/cron.d/container_cronjob
RUN dos2unix /etc/cron.d/container_cronjob

# Script file copied into container. Pay attention to line ending
COPY ./cron_files/script.sh /script.sh
RUN dos2unix /script.sh

# Make sure line ending is correct
RUN dos2unix /usr/src/app/run_crawler.py

# Remove dos2unix and cleanup
RUN apt-get --purge remove -y dos2unix && rm -rf /var/lib/apt/lists/*

# Giving executable permission to script file.
RUN chmod +x /usr/src/app/run_crawler.py
RUN chmod +x /script.sh

# Running commands for the startup of a container.
CMD ["/bin/bash", "-c", "/script.sh && chmod 644 /etc/cron.d/container_cronjob && cron && tail -f /var/log/cron.log"]