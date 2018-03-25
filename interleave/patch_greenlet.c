#include <Python.h>
#include <methodobject.h>

static PyCFunctionWithKeywords my__originalswitch;
static PyTypeObject *my__greenlettype;
static PyObject *my__builtinsmodule;

static PyObject *patched_greenlet_switch(PyObject *self, PyObject *args,
                                         PyObject *kwargs) {
  Py_INCREF(args);
  Py_XINCREF(kwargs);
  PyThreadState *tstate = PyThreadState_Get();
  PyObject *res;
  if (!(tstate->use_tracing)) {
    // if tracing is turned off, turn it on for duration of greenlet switch call
    tstate->use_tracing = 1;
    tstate->tracing--;
    res = my__originalswitch(self, args, kwargs);
    tstate->tracing++;
    tstate->use_tracing = 0;
  } else {
    res = my__originalswitch(self, args, kwargs);
  }
  return res;
}

static PyObject *patch_greenlet_activate(PyObject *self, PyObject *args) {
  my__greenlettype->tp_methods[0].ml_meth =
      (PyCFunction)patched_greenlet_switch;
  Py_RETURN_NONE;
}

static PyObject *patch_greenlet_deactivate(PyObject *self, PyObject *args) {
  my__greenlettype->tp_methods[0].ml_meth = (PyCFunction)my__originalswitch;
  Py_RETURN_NONE;
}

static PyObject *patch_greenlet_is_active(PyObject *self, PyObject *args) {
  if (my__greenlettype->tp_methods[0].ml_meth ==
      (PyCFunction)patched_greenlet_switch) {
    Py_INCREF(Py_True);
    return Py_True;
  } else {
    Py_INCREF(Py_False);
    return Py_False;
  }
}

static PyMethodDef methods[] = {
    {"activate", patch_greenlet_activate, METH_VARARGS,
     "Monkey-patch greenlet.greenlet.switch method."},
    {"deactivate", patch_greenlet_deactivate, METH_VARARGS,
     "Undo monkey-patch greenlet.greenlet.switch method."},
    {"is_active", patch_greenlet_is_active, METH_VARARGS,
     "Return internal state of this module for debugging/testing purposes."},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

PyMODINIT_FUNC initpatch_greenlet(void) {
  PyObject *m;

  m = Py_InitModule("threadmock.patch_greenlet", methods);
  if (m == NULL)
    return;
  my__builtinsmodule = PyEval_GetBuiltins();
  Py_INCREF(my__builtinsmodule);
  my__greenlettype = (PyTypeObject *)PyObject_GetAttrString(
      PyImport_ImportModule("greenlet"), "greenlet");
  if (my__greenlettype == NULL)
    return;
  Py_INCREF(my__greenlettype);
  my__originalswitch =
      (PyCFunctionWithKeywords)(my__greenlettype->tp_methods[0].ml_meth);
}
