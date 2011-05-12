cookbook_file "stars.aashe.org.key" do
  source "ssl/stars.aashe.org.key"
  mode 0640
  owner "root"
  group "root"
end

cookbook_file "/var/www/stars/ssl/stars_combined.crt" do
  source "ssl/stars_combined.crt"
  mode 0640
  owner "root"
  group "root"
end