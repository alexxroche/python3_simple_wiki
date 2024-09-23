# Install Python 3 Simple Wiki

## Prerequisites

##### [Tested on Almalinux 9 and Debian 12] 

`sudo $(which apt dnf yum 2>/dev/null) install -y nginx python3 git`

## Prepare the space
```bash
sudo mkdir -p /var/www
cd /var/www
git clone https://github.com/alexxroche/python3simplewiki.git
mv pythin3simplewiki p3sw
chown -R nginx: p3sw
cd p3sw
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configure nginx

`sudo mkdir -p '/var/www/wiki/static/'`
`sudo touch '/var/www/wiki/static/favicon.ico'`

```bash
sudo mkdir -p /var/www/p3sw/{html,log}
sudo mkdir -p /etc/nginx/sites-available/
sudo mkdir -p /etc/nginx/snippets
sudo touch /etc/nginx/snippets/snakeoil.con

cat >>/etc/nginx/sites-available/p3sw <<EOF
server {
	listen 80;
	listen [::]:80;

    #listen 80 default_server;
    #server_name _;
	server_name localhost wiki.lan;
	index index.html;

    location / {
        # redirect any requests to the same URL but on https
        return 301 https://$host$request_uri;
    }
    return 301 https://$host$request_uri;
}

server {
	# SSL configuration
	#
	listen 443 ssl;
	listen [::]:443 ssl;
	include snippets/snakeoil.con;
	root /var/www/p3sw/html;
	index index.html;

	server_name localhost wiki.lan;

    access_log /var/www/p3sw/log/access.log;
    error_log  /var/www/p3sw/log/error.log;

    location = /favicon.ico { access_log off; log_not_found off; }
	location / {
     if ($request_method = 'OPTIONS') {
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
        add_header 'Access-Control-Max-Age' 1728000;
        add_header 'Content-Type' 'text/plain; charset=utf-8';
        add_header 'Content-Length' 0;
        return 204;
     }
     if ($request_method = 'POST') {
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
     }
     if ($request_method = 'GET') {
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
     }
		# First attempt to serve request as file, then
		# as directory, then fall back to displaying a 404.
		try_files $uri $uri/ =404;
	}

	location ~ /\.ht {
		deny all;
	}

    location /favicon.ico {
        alias /var/www/p3sw/static/favicon.ico;
    }

    location /wiki {
       #allow 127.0.0.0/16;
       #auth_basic "401 Authorization Required";
       #auth_basic_user_file /var/www/p3sw/.htpasswd;
       #deny all;
       try_files           $uri @wiki_home_rewrite;
    }
    location ~ ^/static/([a-z_\.]*[/]*)* {
        try_files           $uri $uri/index.html @wiki_home_rewrite;
    }
    location @wiki_home_rewrite {
        proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header    HTTP_X_REAL_IP $realip_remote_addr;
        proxy_set_header    X-HTTP_REMOTE_IP-Forwarded "$http_x_forwarded_for";
        proxy_set_header    Host $http_host;
        #proxy_set_header    SCRIPT_NAME /wiki;
        proxy_set_header    SCRIPT_NAME /;
        proxy_redirect      off;
        proxy_pass          http://127.0.0.1:8787;
    }
}
EOF
```

## Wiki SystemD
```bash
sudo mkdir -p /etc/systemd/system/
cat >> /etc/systemd/system/p3sw.service <<EOF
[Unit]
Description = py3_simple_flask_wiki
After = network.target

[Service]
PermissionsStartOnly = true
PIDFile = /run/p3sw/wiki.pid
User = nginx
Group = nginx
WorkingDirectory = /var/www/p3sw
ExecStartPre = /bin/mkdir /run/p3sw
ExecStartPre = /bin/chown -R nginx: /run/p3sw
ExecStartPre = /bin/chown -R nginx: /var/www/p3sw/wiki/
ExecStart = /var/www/p3sw/.venv/bin/gunicorn p3sw:app -b 127.0.0.1:8781 -w 3 --pid /run/p3sw/gunicorn.pid
ExecReload = /bin/kill -s HUP $MAINPID
ExecStop = /bin/kill -s TERM $MAINPID
ExecStopPost = /bin/rm -rf /run/p3sw
PrivateTmp = true

[Install]
WantedBy = multi-user.target

EOF
```

## Using git to track history

```bash
sudo chown nginx: -R /var/www/p3sw
sudo git config --global --add safe.directory /var/www/p3sw
```

## Launch the wiki

```bash
sudo systemctl daemon-reload
sudo systemctl enable p3sw; sudo systemctl start p3sw
```

## Supervisor (optional)

If Flask keeps crashing then we can cron a restart twice an hour, or
 install supervisor
`sudo $(which dnf 2>/dev/mull)$(which apt 2>/dev/null) install -y supervisor`

### systemd

```bash
sudo mkdir -p /etc/supervisor/conf.d/
sudo mkdir -p /var/www/p3sw/log
cat >> /etc/supervisor/conf.d/flask_app.conf <<EOF
[program:wiki_supervisor]
#command = /bin/bash /var/www/p3sw/run_flask_app.sh
command = /var/www/p3sw/.venv/bin/gunicorn p3sw:app -b 127.0.0.1:8787 -w 3 --pid /run/p3sw/gunicorn.pid
autostart = true
autorestart = true
user = nginx
stderr_logfile = /var/www/p3sw/log/flask_app.err.log
stdout_logfile = /var/www/p3sw/log/flask_app.out.log
EOF
```
