FROM linuxmintd/mint20.2-amd64

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget python3-pip     \
    && pip3 install --upgrade cryptography  \
    && pip3 install --upgrade chardet       \
    && pip3 install --upgrade urllib3       \
    && pip3 install --upgrade requests      \
    && pip3 install selenium

# Ставим Chrome
# У каждого webdriver есть список версий браузеров с которыми он может работать.
# При обновлении одного из них придётся обновить и второй.
ARG CHROME_VERSION="102.0.5005.115-1"
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb \
  && apt install -y /tmp/chrome.deb                                                                                                                               \
  && rm /tmp/chrome.deb

# Ставим webdriver для этой версии Chrome
ARG DRIVER_VERSION="102.0.5005.61"
RUN wget --no-verbose -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /tmp                                                                                            \
    && mv /tmp/chromedriver /usr/bin/chromedriver                                                                                     \
    && rm /tmp/chromedriver.zip

WORKDIR /tmp/client
RUN chmod 0777 /tmp
COPY imageboard.py .
COPY container_main.py .
COPY named_pipe.py .

# -u == unbuffered output
ENTRYPOINT  ["python3", "-u", "container_main.py"]
