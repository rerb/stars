# thanks eric: http://ericholscher.com/blog/2010/nov/11/building-django-app-server-chef-part-4/

package "rabbitmq-server" do
    :upgrade
end

directory "/etc/init/" do
  owner "root"
  group "root"
  mode "0644"
  action :create
end

cookbook_file "/etc/init/stars-celery.conf" do
    source "celery.conf"
    owner "root"
    group "root"
    mode "0644"
    # notifies :restart, resources(:service => "stars-celery")
end

service "stars-celery" do
    provider Chef::Provider::Service::Upstart
    enabled true
    running true
    supports :restart => true, :reload => true, :status => true
    action [:enable, :start]
end