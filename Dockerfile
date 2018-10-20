FROM python:3.6-stretch
RUN pip install pipenv==11.1.3

RUN apt-get update -yq \
 && apt-get install curl gnupg -yq \
 && curl -sL https://deb.nodesource.com/setup_8.x | bash \
 && apt-get install nodejs -yq \
 && apt-get autoremove -y
RUN npm install -g yarn

WORKDIR /src
RUN touch README.rst CHANGES.rst
COPY Makefile ./

# This part is rebuilt if dependencies change
COPY Pipfile Pipfile.lock setup.py ./
RUN make init

# This part is rebuilt if assets change
COPY assets/ ./assets/
RUN make assets

COPY . .
ENTRYPOINT ["pipenv", "run"]
CMD ["fbctl", "serve"]
