class python3 {
  include wget

  $version = '3.2'
  $packages = ['python3', 'python3-dev']
  package {$packages: ensure => installed}

  if defined(Package['build-essential']) == false {
    package {'build-essential':
      ensure => installed,
    }
  }

  file {'/usr/local/src/': ensure => directory}

  wget::fetch {'distribute':
    source      => 'http://python-distribute.org/distribute_setup.py',
    destination => '/usr/local/src/distribute_setup.py',
    require     => File['/usr/local/src/'],
  }

  exec {'python3-install-distribute':
    path        => '/usr/local/bin:/usr/bin:/bin',
    refreshonly => true,
    command     => 'python3 /usr/local/src/distribute_setup.py',
    require     => [Package['python3'], Wget::Fetch['distribute']],
    subscribe   => Package['python3'],
  }

  exec {'python3-install-pip':
    path        => '/usr/local/bin:/usr/bin:/bin',
    refreshonly => true,
    command     => "easy_install-${version} pip",
    require     => Exec['python3-install-distribute'],
    subscribe   => Exec['python3-install-distribute'],
  }

  exec {'python3-install-venv':
    path        => '/usr/local/bin:/usr/bin:/bin',
    refreshonly => true,
    command     => "pip-${version} install virtualenv",
    require     => Exec['python3-install-pip'],
    subscribe   => Exec['python3-install-distribute'],
  }
}
