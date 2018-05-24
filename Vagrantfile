# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "pxfs/freebsd-11.1"

  config.vm.network "private_network", ip: "10.200.80.100"
  config.vm.network "forwarded_port", guest: 6543, host: 6543
  config.vm.synced_folder ".", "/vagrant", type: "nfs", mount_options: ["actimeo=2"]
  config.ssh.shell = "sh"

  config.vm.provision :shell, privileged: true, inline: <<-EOF
    sysrc hostname=vagrant

    pkg update
    pkg install -y ca_root_nss git-lite curl ntp
    pkg install -y postgresql10-server node redis memcached yarn
    pkg install -y bzip2 sqlite3 gmake
    pkg install -y python36

    ntpd -qg

    sysrc ntpd_enable=YES
    sysrc postgresql_enable=YES
    sysrc redis_enable=YES
    sysrc memcached_enable=YES

    service ntpd start
    service postgresql initdb
    service postgresql start
    service redis start
    service memcached start

    sudo -u postgres createuser -ds vagrant || true
    sudo -u postgres createuser -ds fanboi2 || true
    sh -c 'echo "local all all trust" > /var/db/postgres/data10/pg_hba.conf'
    sh -c 'echo "host all all 127.0.0.1/32 trust" >> /var/db/postgres/data10/pg_hba.conf'
    sh -c 'echo "host all all ::1/128 trust" >> /var/db/postgres/data10/pg_hba.conf'
    service postgresql restart

    fetch -o - https://bootstrap.pypa.io/get-pip.py | /usr/local/bin/python3.6 -
    /usr/local/bin/pip3.6 install pipenv
  EOF

  config.vm.provision :shell, privileged: false, inline: <<-EOF
    echo 'EDITOR=vi; export EDITOR' > $HOME/.profile
    echo 'PAGER=more; export PAGER' >> $HOME/.profile
    echo 'ENV=$HOME/.shrc; export ENV' >> $HOME/.profile
    echo 'LANG=en_US.UTF-8; export LANG' >> $HOME/.profile
    echo 'export PATH' >> $HOME/.profile

    psql template1 -c "CREATE DATABASE fanboi2_dev;"
    psql template1 -c "CREATE DATABASE fanboi2_test;"

    echo 'CELERY_BROKER_URL="redis://127.0.0.1:6379/1"; export CELERY_BROKER_URL' >> $HOME/.profile
    echo 'DATABASE_URL="postgresql://vagrant:@127.0.0.1:5432/fanboi2_dev"; export DATABASE_URL' >> $HOME/.profile
    echo 'MEMCACHED_URL="127.0.0.1:11211"; export MEMCACHED_URL' >> $HOME/.profile
    echo 'REDIS_URL="redis://127.0.0.1:6379/0"; export REDIS_URL' >> $HOME/.profile
    echo 'SERVER_DEV=true; export SERVER_DEV' >> $HOME/.profile
    echo 'SERVER_HOST="0.0.0.0"; export SERVER_HOST' >> $HOME/.profile
    echo 'SERVER_PORT=6543; export SERVER_PORT' >> $HOME/.profile
    echo "SESSION_SECRET=$(openssl rand -hex 32); export SESSION_SECRET" >> $HOME/.profile
    echo "AUTH_SECRET=$(openssl rand -hex 32); export AUTH_SECRET" >> $HOME/.profile

    . $HOME/.profile
    cd /vagrant

    /usr/local/bin/pipenv install --dev
    /usr/local/bin/pipenv run alembic upgrade head

    cd /vagrant/assets
    /usr/local/bin/yarn
    /usr/local/bin/yarn run typings install
    /usr/local/bin/yarn run gulp
  EOF
end
