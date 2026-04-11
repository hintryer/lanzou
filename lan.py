from lanzou.api import LanZouCloud

lzy = LanZouCloud()
cookie = {'ylogin': '984259', 'phpdisk_info': 'WGVVbwVjBzlQZwNqXQ5bNVUMUWIMYFw5AzIBZwU7UGJXZlFmAmdWbAcMAGNdMVBrBm4EMlw2UDYHNQViAzMHNVg9VWEFbwdvUDADMV02WzJVNlEyDDZcPgNiAWYFO1BqVzJRMQI1VmsHMQBZXTZQPwZkBDRcM1A%2FBzQFYAMwBzJYag%3D%3D'}
print(lzy.login_by_cookie(cookie) == LanZouCloud.SUCCESS)
# can get True
folders = lzy.get_move_folders()
print(folders)
