package "apache2" do
    :upgrade
end

package "libapache2-mod-wsgi" do
  :upgrade
end

# Configure Apache

cookbook_file "/etc/apache2/apache2.conf" do
    source "apache2.conf"
    owner "root"
    group "root"
    mode "644"
end

execute "restart apache" do
  command "apache2ctl restart"
end