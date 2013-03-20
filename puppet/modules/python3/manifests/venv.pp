define python3::venv (
  $path        = $title,
  $python      = 'python3',
  $system_site = false,
  $user        = undef
) {
  $opts = $site ? {
    true    => "--system-site-packages",
    default => undef,
  }

  exec {"python3-venv-install-${title}":
    path    => '/usr/local/bin:/usr/bin:/bin',
    command => "virtualenv -p ${python} ${opts} ${path}",
    require => Exec['python3-install-venv'],
    creates => $path,
  }

  if $user != undef {
    exec {"python3-venv-chown-${title}":
      command => "chown -R ${user} ${path}",
      path    => "/usr/local/bin:/usr/bin:/bin",
      require => Exec["python3-venv-install-${title}"],
    }
  }
}
