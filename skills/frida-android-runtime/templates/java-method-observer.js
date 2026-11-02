/*
 * SockBoi reviewed Frida observation template.
 * Replace the example class/method only for an explicitly authorized lab APK.
 * Review the final script, compute its SHA-256, and bind that digest to approval.
 * This template observes call/return events only: it does not alter arguments,
 * return values, control flow, files, network traffic, or security decisions.
 */
'use strict';

Java.perform(function () {
  const className = 'com.example.audit.Target';
  const methodName = 'checkFeature';

  let Target;
  try {
    Target = Java.use(className);
  } catch (error) {
    send({
      type: 'hook_setup',
      status: 'unavailable',
      class_name: className,
      reason: String(error).slice(0, 160)
    });
    return;
  }

  let method;
  try {
    method = Target[methodName];
  } catch (error) {
    send({
      type: 'hook_setup',
      status: 'method_not_found',
      class_name: className,
      method_name: methodName
    });
    return;
  }

  method.overloads.forEach(function (overload, index) {
    const argumentTypes = overload.argumentTypes.map(function (item) {
      return item.className;
    });
    const returnType = overload.returnType.className;

    overload.implementation = function () {
      send({
        type: 'method_enter',
        class_name: className,
        method_name: methodName,
        overload_index: index,
        argument_types: argumentTypes,
        return_type: returnType
      });

      const result = overload.apply(this, arguments);

      send({
        type: 'method_exit',
        class_name: className,
        method_name: methodName,
        overload_index: index,
        returned: true
      });
      return result;
    };
  });

  send({
    type: 'hook_setup',
    status: 'attached',
    class_name: className,
    method_name: methodName,
    overload_count: method.overloads.length
  });
});
