#create a function CreateUser that takes in a request and returns a rendered template for creating a new user. The function should check if the request method is POST, and if so, it should create a new user with the provided username and password. If the request method is GET, it should render the new user creation form.
def CreateUser(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Create the new user
        user = user.objects.create_user(username=username, password= password)
        user.save()
        return redirect('index')  # Redirect to the index page after successful user creation
    else:
        return render(request, 'app/new.html', {})  # Render the new user creation form 
    