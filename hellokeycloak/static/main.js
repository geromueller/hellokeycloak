const keycloak = new Keycloak(keycloakConfig);

function update() {
  document.getElementById("login").disabled = keycloak.authenticated;
  document.getElementById("logout").disabled = !keycloak.authenticated;

  const frontend = document.getElementById("frontend");
  const backend = document.getElementById("backend");
  if (keycloak.authenticated) {
    frontend.innerHTML =
      "Email: " +
      keycloak.tokenParsed.email +
      "\nRoles: \n" +
      JSON.stringify(keycloak.tokenParsed.resource_access, null, 2);

    backend.innerHTML = "loading...";
    fetch("/me", {
      method: "GET",
      headers: {
        Authorization: "Bearer " + keycloak.token,
      },
    })
      .then((Result) => {
        Result.json().then((obj) => {
          backend.innerHTML =
            "Email: " +
            obj.email +
            "\nRoles:\n" +
            JSON.stringify(obj.roles, null, 2);
        });
      })
      .catch((errorMsg) => {
        console.log(errorMsg);
      });
  } else {
    frontend.innerHTML = "";
    backend.innerHTML = "";
  }
}

window.onload = function () {
  document.getElementById("keycloak").innerHTML = JSON.stringify(
    keycloakConfig,
    null,
    2
  );

  console.log("setup keycloak callbacks");
  keycloak.onAuthSuccess = function () {
    console.log("auth success");
    update();
  };

  keycloak.onAuthLogout = function () {
    console.log("auth logout");
    update();
  };

  keycloak.onAuthError = function (errorData) {
    console.log("auth error");
    update();
  };

  console.log("init keycloak");
  keycloak
    .init(keycloakInitOptions)
    .then(function (authenticated) {
      console.log(
        keycloak.authenticated ? "authenticated" : "not authenticated"
      );
    })
    .catch(function (error) {
      console.log("failed to initialize " + error.error);
    });
  console.log("loading done");
};
