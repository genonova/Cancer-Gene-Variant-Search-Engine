# Search Engine
   * Dependencies:
       1. Redis

## Django Set Up
## Tutorial
* Please follow this tutorial [Taskbuster - Non official but REALLY GOOD](http://www.marinamele.com/taskbuster-django-tutorial/taskbuster-working-environment-and-start-django-project)
before you proceed to next steps
    * Please not that you need to set up the following parts
        * `settings_test.py` under `settings/` folder
            * Apply for a MySQL user account for the AWS server from Dev Ops
            * Configure the `DATABASES` environment variable to connect to the database
        * Two environment variables must be set up (in later sections):
            1. `DJANGO_SETTINGS_MODULE`
            2. `DJANGO_SECRET_KEY`
        * \[Temporary\] Go to `static/demo/search_cancer` folder and follow the `README.MD` to download the `vendor`
        
### Environment Set Up
* [Follow this link to set up virtual environment and wrapper](http://roundhere.net/journal/virtualenv-ubuntu-12-10/)
    * Commands:
        * `sudo apt-get install python-pip`
        * `sudo pip install virtualenv`
        * `mkdir ~/.virtualenvs`
        * `sudo pip install virtualenvwrapper`
        * `export WORKON_HOME=~/.virtualenvs`
        * Add this line to the end of ~/.bashrc or /root/.bashrc so that the virtualenvwrapper commands are loaded.
            * `. /usr/local/bin/virtualenvwrapper.sh`
        * `mkvirtualenv myawesomeproject`
        * `workon myawesomeproject`
 

### To Run Server
0. Please read #Environment first 
1. On Amazon EC2
    * Make sure root user has same virtual environment and workon command 
    * Config the postactive / postdeactive scripts under `$VIRTUAL_ENV/bin` (in virtualenv mode)
        * postactive:
            * `export DJANGO_SETTINGS_MODULE="settings.settings_test"`
            * `export DJANGO_SECRET_KEY="xxxxxx"` (the secrete key is masked)
        * postdeactive:
            * `unset DJANGO_SETTINGS_MODULE`
            * `unset DJANGO_SECRET_KEY`
    * Check if the two environment exists (you may need to reactivate the env by `workon xxx`)
    * First 'sudo su' then work on the created environment
    * `python manage.py runserver 0.0.0.0:80`

### Internationalization
* Go to the `locale` folder and see the instructions
### Static Files
* For local test, please make sure `DEBUG=True` in your `settings_test.py` file
## Deploy On Server
* Follow this [Tutorial](http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/) with `Nginx` & `Supervisor` & `Gunicorn`
    * Gunicorn script : `search_engine/gunicorn_start`
    * Supervisor script : ` /etc/supervisor/conf.d/search_engine.conf`
    * Nginx config file : `/etc/nginx/sites-available/search_engine`
    * Logs under `search_engine/logs/`
        * `gunicorn_supervisor.log `
        * `gunicorn.log`
        * `nginx-access.log`
        * `nginx-error.log`

