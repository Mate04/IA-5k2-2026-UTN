### 5.1 La consulta intermedia y su validación

La misma validación vale para los dos modos. Primero se chequea la forma con JSON Schema. Después, la semántica: cantidad de clases según la intención, clases dentro del vocabulario, predicado o atributo presente. Una consulta con problemas no se ejecuta: se responde `unsupported` y se informa el motivo.
