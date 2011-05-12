# Thanks, Eric: http://ericholscher.com/blog/2010/nov/10/building-django-app-server-chef-part-3/
# for the starting point

package "nginx" do
    :upgrade
    action
end

# Set up Nginx Service
service "nginx" do
  enabled true
  running true
  supports :status => true, :restart => true, :reload => true
  action [:enable, :stop]
end

# General Settings
cookbook_file "/etc/nginx/nginx.conf" do
  source "nginx.conf"
  mode 0640
  owner "root"
  group "root"
end

cookbook_file "/etc/nginx/proxy.conf" do
  source "proxy.conf"
  mode 0640
  owner "root"
  group "root"
end

# Individual Site Configurations
node["nginx"]["sites"].each do |site|
  
  template_vars = {}
  if( site.key?("ssl_cert") and site.key?("ssl_key") and site.key?('ssl_root'))
    
    template_vars = {
      :cert_path => "#{site["ssl_root"]}#{site['ssl_cert']}",
      :key_path => "#{site["ssl_root"]}#{site['ssl_key']}"
    }
  end
  
  template "/etc/nginx/sites-enabled/#{site['name']}" do
    source "#{site['name']}.erb"
    mode 0640
    owner "root"
    group "root"    
    variables(
      template_vars
    )
  end
  
  # create ssl directory if the root path is specified
  if site.key?("ssl_root")
    directory site["ssl_root"] do
      owner "root"
      group "root"
      mode "0755"
      recursive true
      not_if do
        File.exists?(site["ssl_root"])
      end
    end
  end

  # add the cert if specified
  ["ssl_cert", "ssl_key"].each do |ssl_file|
    if site.key?(ssl_file)
      cookbook_file "#{site['ssl_root']}#{site[ssl_file]}" do
        owner "root"
        group "root"
        mode "0755"
      end
    end
  end
end

# Set up Nginx Service
service "nginx" do
  action [:start]
end