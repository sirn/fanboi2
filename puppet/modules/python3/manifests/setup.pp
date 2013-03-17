define python3::setup ($setup, $mode='install', $venv, $python='python3') {
  exec {"python3-setup-${title}":
    path        => "${venv}/bin:/usr/local/bin:/usr/bin:/bin",
    command     => "${python} ${setup} ${mode}",
    environment => ['LANG=en_US.UTF-8'], # Fix Unicode error with Python 3.
    timeout     => 0,
  }
}
