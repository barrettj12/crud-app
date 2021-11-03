# `crud-app`

`crud-app` is a simple database application which allows the user to create, view, modify and delete tables. Tables can optionally be password-protected. You can try it out [here](https://barrettj12.github.io/crud-app/).

---

The frontend is written in HTML, CSS and JavaScript, and hosted [here](https://barrettj12.github.io/crud-app/) using GitHub Pages.

The backend is written in Python using the Flask web framework. It consists of [an API](https://barrettj12-crud-app.herokuapp.com/) hosted on Heroku, to which the frontend sends HTTP requests to operate on the data. [Gunicorn](https://gunicorn.org/) is used to deploy the backend server.

The data itself is all hosted on Heroku in a PostgreSQL database, using the [Heroku Postgres](https://www.heroku.com/postgres) add-on. The backend communicates to this database using the [psycopg2](https://www.psycopg.org/) package.

---

Contributors: [@barrettj12](https://github.com/barrettj12)