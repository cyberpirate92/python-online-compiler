from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from . import forms
from .CompilerUtils import Compiler,TestCase,Language

# Create your views here.
def testpage(request):
    template_data = {}
    if request.method == 'POST':
        form = forms.CodeExecutorForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            input_data = form.cleaned_data['input']
            expected_output = form.cleaned_data['output']
            testcase = TestCase(input_data,expected_output)
            lan = Language(int(form.cleaned_data['language']))
            has_template = form.cleaned_data['has_template']
            if has_template:
                code_template = form.cleaned_data['template']
            if len(input_data) == 0 or input_data is None:
                template_data['error'] = "Invalid code"
                return render(request,'generic_error.html',template_data)
            else:
                if lan == Language.PYTHON:
                    executor = Compiler()
                    executor.setCode(code)
                    executor.setLanguage(lan)
                    executor.addTestCase(testcase)
                    if has_template:
                        executor.setTemplate(code_template)
                    executor.execute()
                    executor.deleteCodeFile()
                    if executor.hasExecuted:
                        if executor.hasErrors:
                            template_data['error'] = executor.getErrors()[0]
                        else:
                            template_data['error'] = "No errors :)"
                        template_data['output'] = executor.getOutput()[0]
                        return render(request,'OutputView.html',template_data)
                    else:
                        return render(request,'generic_error.html',{'error':'Sorry! Execution failed'})
        else:
            return HttpResponse("Cannot sanitize form data")
    else:
        form = forms.CodeExecutorForm()
        template_data['form'] = form
        return render(request,'test-compiler.html',template_data)