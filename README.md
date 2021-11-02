# `crud-app`

Frontend:
 - HTML
 - Hosted on GitHub pages at https://barrettj12.github.io/crud-app/

Backend: 
 - Python
 - Flask
 - Gunicorn
 - The API is hosted on Heroku at https://barrettj12-crud-app.herokuapp.com/


Server defaults to `https://barrettj12-crud-app.herokuapp.com` but you can
override this by making a file `/docs/server.js` which contains
```js
const LOCAL_SERVER = <your-desired-server-without-trailing-slash>
```