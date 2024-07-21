# Python adapter for Auth.js

The Python Adapter for Auth.js project migrates the PostgreSQL adapter from TypeScript to Python, enabling seamless integration of Auth.js with Python applications. It includes a REST API using SqlAclhemy, Pydantic and Redis for session storage.

### Contributing
Before you start, make sure you have Docker and Docker Compose installed on your machine.

1. Clone the repository
```bash
git clone https://github.com/mr-raccoon-97/python-adapter-for-auth.js.git
cd python-adapter-for-auth.js
```

2. Run tests with the following command:
```bash
docker-compose --profile tests up --build --exit-code-from python-tests
```

3. Run the api in development mode with the following command:
```bash
docker-compose --profile dev up --build
```

Go to `http://0.0.0.0:8000/docs` to see the Swagger documentation.

![alt text](swagger.png)

4. Add the following [adapter](rest-adapter.ts) to your Auth.js project as stated in the [documentation](https://next-auth.js.org/getting-started/introduction). (The Auth.js documentation is very obscure, so I recommend you to try other adapters first, like the pg-adapter, to setup an adapter). In the [auth.ts](https://authjs.dev/getting-started/installation?framework=next.js) file:

```typescript

import NextAuth from "next-auth"
import Google from "next-auth/providers/google"
import RestAdapter from "./rest-adapter"

export const { handlers, signIn, signOut, auth } = NextAuth({
    adapter: RestAdapter(),
    providers: [Google],
})

```

To clean up the containers:
```bash
docker compose down -v --remove-orphans
```

### Note
The database schemas in this projects differ from the original Auth.js project, and I'm planning to change them even more, since they have a very poor design, (that's the idea of adapters, right?). For example, I used Redis for sessions and tokens storage, for better performance and automatic expiration.

I will be adding ports to make the infrastructure pluggable into the controller, so you can use the same controller with different adapters.

While the project is already tested and functional, it is still in development. You should setup the project in a production environment at your own risk. I don't make any guarantees about the project's stability, security, or performance, and I am not responsible for any damages that may occur from using this project. Don't forget to update the middleware in the [api.py](api.py) file to secure your API, since the current is open to the public for development purposes.

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Contact
If you have any questions, feel free to contact me at curious.mr.fox.97@gmail.com. Feel free to contribute and enhance the project.
