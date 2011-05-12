# Create the application root

directory node["webapp_paths"]["webapp_path"] do
  owner "www-data"
  group "www-data"
  mode "0755"
  recursive true
  action :create
end

directory "#{node["webapp_paths"]["webapp_path"]}/logs" do
  owner "www-data"
  group "www-data"
  mode "0755"
  recursive true
  action :create
end

directory "#{node["webapp_paths"]["webapp_path"]}/ssl" do
  owner "www-data"
  group "www-data"
  mode "0755"
  recursive true
  action :create
end

directory node["webapp_paths"]["media_symlink_root"] do
  owner "www-data"
  group "www-data"
  mode "0755"
  recursive true
  action :create
end

# Symlink all the media links
# Create the targets if they don't exist
node["webapp_paths"]["media_links"].each_pair do |link, name|
    directory link do
      owner "www-data"
      group "www-data"
      mode "0755"
      recursive true
      action :create
      not_if do
        File.exists?(link)
      end
    end
    link "#{node['webapp_paths']['media_symlink_root']}#{name}" do
      to "#{link}"
    end
end

