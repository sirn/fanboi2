# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "phusion/ubuntu-14.04-amd64"
  config.vm.network :forwarded_port, guest: 6543, host: 6543

  config.vm.provision :shell, privileged: true, inline: <<-EOF
    sudo apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 7FCC7D46ACCC4CF8
    sudo apt-get clean
    sudo rm -rf /var/lib/apt/lists/*
    sudo rm -rf /var/lib/apt/lists/partial/*
    sudo apt-get clean

    sudo apt-get -y update
    sudo apt-get -y install curl
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    curl -sL https://deb.nodesource.com/setup | sudo bash -
    sudo add-apt-repository ppa:rwky/redis
    sudo apt-get -y update

    sudo apt-get -y install git-core
    sudo apt-get -y install build-essential zlib1g-dev
    sudo apt-get -y install postgresql-9.2 postgresql-client-9.2 libpq-dev
    sudo apt-get -y install redis-server
    sudo apt-get -y install memcached
    sudo apt-get -y install nodejs

    sudo -u postgres createuser -ds vagrant || true
    sudo -u postgres createuser -ds fanboi2 || true
    sudo sh -c 'echo "local all all trust" > /etc/postgresql/9.2/main/pg_hba.conf'
    sudo sh -c 'echo "host all all 127.0.0.1/32 trust" >> /etc/postgresql/9.2/main/pg_hba.conf'
    sudo sh -c 'echo "host all all ::1/128 trust" >> /etc/postgresql/9.2/main/pg_hba.conf'
    sudo service postgresql restart
  EOF

  config.vm.provision :shell, privileged: false, inline: <<-EOF
    cd /tmp
    rm -rf $HOME/pypy3
    curl -sL https://bitbucket.org/pypy/pypy/downloads/pypy3-2.3.1-linux64.tar.bz2 | tar -xjf -
    mv pypy3*/ $HOME/pypy3
    curl -sL https://bootstrap.pypa.io/ez_setup.py | $HOME/pypy3/bin/pypy
    curl -sL https://bootstrap.pypa.io/get-pip.py | $HOME/pypy3/bin/pypy
    echo '. "$HOME/.bashrc"' > $HOME/.profile
    echo 'export PATH="$HOME/nodejs/bin:$HOME/pypy3/bin:$HOME/bin:$PATH"' >> $HOME/.profile

    npm config set prefix $HOME/nodejs
    npm install -g brunch

    psql template1 -c "CREATE DATABASE fanboi2_development;"
    psql template1 -c "CREATE DATABASE fanboi2_test;"

    cd /vagrant
    rm -rf fanboi2.egg-info
    rm -rf node_modules
    cp development.ini.sample development.ini
    cp alembic.ini.sample alembic.ini
    $HOME/pypy3/bin/pypy setup.py develop
    $HOME/pypy3/bin/alembic upgrade head
    npm install
    $HOME/nodejs/bin/brunch build
  EOF
end
