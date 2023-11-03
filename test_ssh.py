import paramiko

ssh = paramiko.SSHClient()
ssh.connect( '192.168.1.11', username = 'root', password = '123456' )
ssh.exec_command( 'ls -al' )