#include <Python.h>
#include <methodobject.h>

static PyObject *my__error;
static PyObject *my__originalvalues;
static PyObject *my__builtinsmodule;

// FIXME: this monkey patching is not working when patched function
// is used as a key in some dict - it then causes memory corruption errors

static PyObject *patched_function(PyObject *self, PyObject *args) {
  return PyObject_CallObject(self, args);
}

static PyObject *patch_c_func_internal_state(PyObject *self, PyObject *args) {
  return my__originalvalues;
}

static PyObject *patch_c_func_patch(PyObject *self, PyObject *args) {
  PyObject *arg;
  PyObject *newfunc;
  if (!PyArg_ParseTuple(args, "OO:patch", &arg, &newfunc))
    return NULL;
  if (!PyObject_IsInstance(arg, &PyCFunction_Type)) {
    PyErr_SetString(
        PyObject_GetAttrString(my__builtinsmodule, "TypeError"),
        "Wrong argument type, 'builtin_function_or_method' was expected.");
    return NULL;
  }
  PyCFunctionObject *func = arg;
  if (func->m_self != NULL) {
    PyErr_SetString(PyObject_GetAttrString(my__builtinsmodule, "TypeError"),
                    "Bad argument, only unbound methods and functions are "
                    "currently supported.");
    return NULL;
  }
  PyDict_SetItem(my__originalvalues, Py_BuildValue("i", (int)(func)),
                 Py_BuildValue("i", (int)(func->m_ml->ml_meth)));
  func->m_ml->ml_meth = patched_function;
  func->m_self = newfunc;
  Py_INCREF(newfunc);
  Py_RETURN_NONE;
}

static PyObject *patch_c_func_unpatch(PyObject *self, PyObject *args) {
  PyObject *arg;
  if (!PyArg_ParseTuple(args, "O:helloworld", &arg))
    return NULL;

  if (!PyObject_IsInstance(arg, &PyCFunction_Type)) {
    PyErr_SetString(
        PyObject_GetAttrString(my__builtinsmodule, "TypeError"),
        "Wrong argument type, 'builtin_function_or_method' was expected.");
    return NULL;
  }
  PyCFunctionObject *func = arg;
  PyObject *func_pointer_pyint =
      PyDict_GetItem(my__originalvalues, Py_BuildValue("i", (int)(func)));
  if (func_pointer_pyint == NULL) {
    printf("SOMETHING WENT WRONG\n");
    return NULL;
  }
  PyDict_DelItem(my__originalvalues, Py_BuildValue("i", (int)(func)));
  int func_pointer_int = PyInt_AsLong(func_pointer_pyint);
  func->m_ml->ml_meth = func_pointer_int;
  Py_DECREF(func->m_self);
  func->m_self = NULL;
  Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
    {"patch", patch_c_func_patch, METH_VARARGS,
     "Monkey-patch a 'builtin_function_or_method' object's underlying function "
     "pointer with any python callable."},
    {"unpatch", patch_c_func_unpatch, METH_VARARGS,
     "Undo monkey-patch on a 'builtin_function_or_method'."},
    {"internal_state", patch_c_func_internal_state, METH_VARARGS,
     "Return internal state of this module for debugging/testing purposes."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

PyMODINIT_FUNC initpatch_c_func(void) {
  PyObject *m;

  m = Py_InitModule("interleave.patch_c_func", methods);
  if (m == NULL)
    return;
  my__error = PyErr_NewException("patch_c_func.Error", NULL, NULL);
  Py_INCREF(my__error);
  my__builtinsmodule = PyEval_GetBuiltins();
  Py_INCREF(my__builtinsmodule);
  my__originalvalues = PyObject_CallFunction(
      PyDict_GetItemString(my__builtinsmodule, "dict"), NULL);
  if (my__originalvalues == NULL)
    return;
  Py_INCREF(my__originalvalues);
  PyModule_AddObject(m, "Error", my__error);
}
