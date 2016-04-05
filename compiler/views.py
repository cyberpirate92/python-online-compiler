from django.shortcuts import render
from django.http import HttpResponse
from . import forms
from . import CompilerUtils
from .CompilerUtils import Compiler, Language


# Create your views here.
def testpage(request):
    template_data = {}
    if request.method == 'POST':
        form = forms.CodeExecutorForm(request.POST)
        if form.is_valid():
            executor = Compiler()
            code = form.cleaned_data['code']
            input_data = form.cleaned_data['input']
            expected_output = form.cleaned_data['output']
            test_cases = CompilerUtils.generate_test_cases(input_data, expected_output)
            for test_case in test_cases:
                executor.add_test_case(test_case)
            lan = Language(int(form.cleaned_data['language']))
            has_template = form.cleaned_data['has_template']
            if has_template:
                code_template = form.cleaned_data['template']
            if len(input_data) == 0 or input_data is None:
                template_data['error'] = "Invalid code"
                return render(request, 'generic_error.html', template_data)
            else:
                if lan == Language.PYTHON:
                    executor.set_code(code)
                    executor.set_language(lan)
                    if has_template:
                        executor.set_template(code_template)
                    execution_result = executor.execute()
                    template_data['result'] = execution_result.name
                    executor.delete_code_file()
                    if executor.hasExecuted:
                        checked_values = executor.compare_outputs()
                        display_data = []
                        outputs = executor.get_output()
                        errors = executor.get_errors()
                        for i in range(len(outputs)):
                            if executor.hasErrors:
                                e = errors[i]
                            else:
                                e = "No errors!"
                            temp_tuple = (i+1, checked_values[i], outputs[i], e)
                            display_data.append(temp_tuple)
                        template_data['display_data'] = display_data
                        return render(request, 'OutputView.html', template_data)
                    else:
                        return render(request, 'generic_error.html', {'error': 'Sorry! Execution failed'})
        else:
            return HttpResponse("Cannot sanitize form data")
    else:
        form = forms.CodeExecutorForm()
        template_data['form'] = form
        return render(request, 'test-compiler.html', template_data)