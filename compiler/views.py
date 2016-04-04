from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from . import forms
from . import CompilerUtils
from .CompilerUtils import Compiler,TestCase,Language

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
            test_cases = CompilerUtils.generateTestCases(input_data,expected_output)
            for testcase in test_cases:
                executor.addTestCase(testcase)
            lan = Language(int(form.cleaned_data['language']))
            has_template = form.cleaned_data['has_template']
            if has_template:
                code_template = form.cleaned_data['template']
            if len(input_data) == 0 or input_data is None:
                template_data['error'] = "Invalid code"
                return render(request,'generic_error.html',template_data)
            else:
                if lan == Language.PYTHON:
                    executor.setCode(code)
                    executor.setLanguage(lan)
                    executor.addTestCase(testcase)
                    if has_template:
                        executor.setTemplate(code_template)
                    executor.execute()
                    executor.deleteCodeFile()
                    if executor.hasExecuted:
                        checked_values = executor.checkOutputs()

                        for i in range(len(checked_values)):
                            if checked_values[i]:
                                template_data['t'+str(i)] = "success!"
                            else:
                                template_data['t'+str(i)] = "failed!"

                        for i in range(len(executor.getOutput())):
                            if executor.hasErrors:
                                template_data['error'+str(i)] = executor.getErrors()[i]
                            else:
                                template_data['error'+str(i)] = "No errors :)"
                            template_data['output'+str(i)] = executor.getOutput()[i]

                        return render(request,'OutputView.html',template_data)
                    else:
                        return render(request,'generic_error.html',{'error':'Sorry! Execution failed'})
        else:
            return HttpResponse("Cannot sanitize form data")
    else:
        form = forms.CodeExecutorForm()
        template_data['form'] = form
        return render(request,'test-compiler.html',template_data)