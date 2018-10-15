# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "generic/freebsd11"

  config.vm.network "private_network", ip: "10.200.80.100"
  config.vm.network "forwarded_port", guest: 6543, host: 6543
  config.vm.synced_folder ".", "/vagrant", type: "nfs", mount_options: ["actimeo=2"]
  config.ssh.shell = "sh"

  # Locking pipenv version to 2018.6.25 because of issue with shell detection:
  # https://github.com/sarugaku/shellingham/issues/15
  config.vm.provision :shell, privileged: true, inline: <<-EOF
    sysrc hostname=vagrant

    pkg update
    pkg install -y ca_root_nss git-lite curl ntp bash
    pkg install -y postgresql10-server node8 npm-node8 redis memcached
    pkg install -y bzip2 sqlite3 gmake
    pkg install -y python36 py36-pip py36-pipenv
    npm install -g yarn

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
  EOF

  config.vm.provision :shell, privileged: false, inline: <<-EOF
    echo 'EDITOR=vi; export EDITOR' > $HOME/.profile
    echo 'PAGER=more; export PAGER' >> $HOME/.profile
    echo 'ENV=$HOME/.shrc; export ENV' >> $HOME/.profile
    echo 'LANG=en_US.UTF-8; export LANG' >> $HOME/.profile
    echo 'PIPENV=pipenv-3.6; export PIPENV' >> $HOME/.profile

    psql template1 -c "CREATE DATABASE fanboi2_dev;"
    psql template1 -c "CREATE DATABASE fanboi2_test;"

    . $HOME/.profile

    echo 'CELERY_BROKER_URL="redis://127.0.0.1:6379/1"' > /vagrant/.env
    echo 'DATABASE_URL="postgresql://vagrant:@127.0.0.1:5432/fanboi2_dev"' >> /vagrant/.env
    echo 'MEMCACHED_URL="127.0.0.1:11211"' >> /vagrant/.env
    echo 'REDIS_URL="redis://127.0.0.1:6379/0"' >> /vagrant/.env
    echo 'SERVER_DEV=true' >> /vagrant/.env
    echo 'SERVER_HOST="0.0.0.0"' >> /vagrant/.env
    echo 'SERVER_PORT=6543' >> /vagrant/.env
    echo "SESSION_SECRET=$(openssl rand -hex 32)" >> /vagrant/.env
    echo "AUTH_SECRET=$(openssl rand -hex 32)" >> /vagrant/.env

    cd /vagrant
    make develop
    make migrate
  EOF
end
