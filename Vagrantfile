# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "pxfs/freebsd-10.3"
  config.vm.synced_folder ".", "/vagrant", nfs: true, mount_options: ['actimeo=2']
  config.vm.network :forwarded_port, guest: 6543, host: 6543
  config.vm.network :forwarded_port, guest: 9000, host: 9000
  config.ssh.shell = "sh"

  config.vm.provision :shell, privileged: true, inline: <<-EOF
    pkg install -y ca_root_nss
    pkg install -y git-lite
    pkg install -y postgresql95-server
    pkg install -y node
    pkg install -y redis
    pkg install -y memcached
    pkg install -y bzip2 sqlite3 gmake
    pkg install -y python27 python36

    sysrc postgresql_enable=YES
    sysrc redis_enable=YES
    sysrc memcached_enable=YES

    service postgresql initdb
    service postgresql start
    service redis start
    service memcached start

    sudo -u pgsql createuser -ds vagrant || true
    sudo -u pgsql createuser -ds fanboi2 || true
    sh -c 'echo "local all all trust" > /usr/local/pgsql/data/pg_hba.conf'
    sh -c 'echo "host all all 127.0.0.1/32 trust" >> /usr/local/pgsql/data/pg_hba.conf'
    sh -c 'echo "host all all ::1/128 trust" >> /usr/local/pgsql/data/pg_hba.conf'
    service postgresql restart

    fetch -o - https://bootstrap.pypa.io/get-pip.py | /usr/local/bin/python3.6 -
    /usr/local/bin/pip3.6 install virtualenv
  EOF

  config.vm.provision :shell, privileged: false, inline: <<-EOF
    virtualenv -p python3.6 $HOME/python3.6

    mkdir $HOME/yarn
    curl -sL https://yarnpkg.com/latest.tar.gz | tar -xvzf - -C $HOME/yarn --strip 1

    echo 'EDITOR=vi; export EDITOR' > $HOME/.profile
    echo 'PAGER=more; export PAGER' >> $HOME/.profile
    echo 'ENV=$HOME/.shrc; export ENV' >> $HOME/.profile
    echo 'PATH="$HOME/yarn/bin:$PATH"' >> $HOME/.profile
    echo 'PATH="$HOME/python3.6/bin:$PATH"' >> $HOME/.profile
    echo 'PATH="$HOME/bin:$PATH"' >> $HOME/.profile
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

    cd /vagrant
    $HOME/python3.6/bin/pip3 install -e .
    $HOME/python3.6/bin/alembic upgrade head

    cd /vagrant/assets
    env PYTHON=/usr/local/bin/python2.7 $HOME/yarn/bin/yarn
    $HOME/yarn/bin/yarn run typings install
    $HOME/yarn/bin/yarn run gulp
  EOF
end
