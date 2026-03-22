# Snippets

## create a new uuid named directory and cd into it
- commands
  ```sh
  mkdir $(node -e "console.log(crypto.randomUUID())")
  ```
  or 
  ```sh
  mkdir $(uuidgen)
  ```
  or 
  ```sh
  id=$(node -e "console.log(crypto.randomUUID())")
  mkdir "$id"
  cd "$id"
  ```
  
  or 
  ```sh
  id=$(node -e 'console.log(crypto.randomUUID())') && mkdir "$id" && cd "$id"
  ```
  or
  ```sh
  id=$(uuidgen) && mkdir "$id" && cd "$id"
  ```
  
