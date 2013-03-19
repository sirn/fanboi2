class supervisord {
  package {'supervisor': ensure => installed}
  service {'supervisor':
    enable     => true,
    ensure     => running,
    hasrestart => false,
    require    => Package['supervisor'],
  }
}
