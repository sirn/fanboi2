class supervisord::inet ($port=":9001") {
  $config_dir = '/etc/supervisor/conf.d/'

  file {"${config_dir}_inet.conf":
    ensure  => file,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => template('supervisord/inet.conf.erb'),
    require => Package['supervisor'],
    notify  => Service['supervisor'],
  }
}
