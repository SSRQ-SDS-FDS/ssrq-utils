use feruca::Collator;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

/// Sorts a list of strings using the Unicode Collation Algorithm.
///
/// # Arguments
///
/// * `inputs` - A vector of strings to be sorted.
///
/// # Returns
///
/// A `PyResult` containing a vector of sorted strings.
///
/// # Errors
///
/// This function will return an error if the collation process fails.
///
#[pyfunction]
fn uca_simple_sort(mut inputs: Vec<String>) -> PyResult<Vec<String>> {
    let mut collator = Collator::default();
    inputs.sort_unstable_by(|a, b| collator.collate(a, b));
    Ok(inputs)
}

/// Sorts a list of Python objects using the Unicode Collation Algorithm.
///
/// # Arguments
///
/// * `objects` - A vector of Python objects to be sorted.
/// * `method_name` - The name of the method to call on each object to retrieve the string for comparison.
/// * `args` - Optional arguments to pass to the method.
///
/// # Returns
///
/// A `PyResult` containing a vector of sorted Python objects.
///
/// # Errors
///
/// This function will return an error if the collation process fails or if the method call on the Python objects fails.
///
#[pyfunction]
#[pyo3(signature = (objects, method_name, args=None))]
fn uca_complex_sort(
    objects: Vec<Py<PyAny>>,
    method_name: &str,
    args: Option<Vec<Py<PyAny>>>,
) -> PyResult<Vec<Py<PyAny>>> {
    let mut collator = Collator::default();
    let mut values: Vec<(String, Py<PyAny>)> = Python::with_gil(|py| {
        objects
            .into_iter()
            .map(|obj| {
                let value: String = match &args {
                    Some(args) => obj
                        .call_method1(py, method_name, PyTuple::new(py, args.as_slice()).unwrap())
                        .unwrap()
                        .extract(py)
                        .unwrap(),
                    None => obj
                        .call_method0(py, method_name)
                        .unwrap()
                        .extract(py)
                        .unwrap(),
                };
                (value, obj)
            })
            .collect()
    });

    values.sort_unstable_by(|a, b| collator.collate(&a.0, &b.0));
    Ok(values.into_iter().map(|(_, obj)| obj).collect())
}

/// A Python module implemented in Rust.
#[pymodule]
fn _pyferuca(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(uca_simple_sort, m)?)?;
    m.add_function(wrap_pyfunction!(uca_complex_sort, m)?)?;
    Ok(())
}
