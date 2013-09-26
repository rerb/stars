;; Additional Emacs config for STARS.
((python-mode
  (python-shell-interpreter . "python")
  (python-shell-interpreter-args
   . "/Users/rerb/src/aashe/stars/manage.py shell")
  (python-shell-prompt-regexp . "In \\[[0-9]+\\]: ")
  (python-shell-prompt-output-regexp . "Out\\[[0-9]+\\]: ")
  (python-shell-completion-setup-code
   . "from IPython.core.completerlib import module_completion")
  (python-shell-completion-module-string-code
   . "';'.join(module_completion('''%s'''))\n")
  (python-shell-completion-string-code
   . "';'.join(get_ipython().Completer.all_completions('''%s'''))\n")
  (python-shell-extra-pythonpaths
   "/Users/rerb/.virtualenvs/stars/lib/python2.7/site-packages"
   "/Users/rerb/.virtualenvs/stars/src/aashe-python")
  (python-shell-virtualenv-path . "/Users/rerb/.virtualenvs/stars")
  (python-shell-process-environment
   "MEDIA_ROOT=/Users/rerb/src/aashe/app_media/stars/"
   "STARS_MYSQL_DB_URL=mysql://root@localhost/stars20130816"
   "ISS_MYSQL_DB_URL=mysql://root@localhost/iss20130816"
   "STARS_SQLITE_DB_URL=sqlite:////Users/rerb/sqlite/stars.db"
   "ISS_SQLITE_DB_URL=sqlite:////Users/rerb/sqlite/iss.db"
   "STARS_DB_URL=mysql://root@localhost/stars20130816"
   "ISS_DB_URL=mysql://root@localhost/iss20130816"
   "STARS_TEST_DB=sqlite:////Users/rerb/sqlite/stars.db"
   "ISS_TEST_DB=sqlite:////Users/rerb/sqlite/iss.db")))
