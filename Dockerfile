FROM python:3.6-stretch
RUN pip install pipenv==11.1.3

RUN apt-get update -yq \
 && apt-get install curl gnupg -yq \
 && curl -sL https://deb.nodesource.com/setup_8.x | bash \
 && apt-get install nodejs -yq \
 && apt-get autoremove -y
RUN npm install -g yarn

WORKDIR /src
COPY Makefile ./

COPY setup.py setup.cfg ./
RUN make build

COPY . .
RUN make assets

ENTRYPOINT ["make"]
CMD ["serve"]
