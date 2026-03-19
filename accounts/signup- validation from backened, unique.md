signup- validation from backened, unique email, strong password, check passwprd, email verification(two factor authentication via OTP)
login- validation from backend, check email and password, rate limit(wrong password attempt 5 after that blocked)
home page- dynamic content, change password,logout
change password- validation , check not old password, reset password 
logout- after logut redirect to login , after logout no rollback to homepage ( custom middleware authentication )
forget password- first email verify before resetting password via otp. then set new password.

key point-middleware, rate limit , backened validation,email verification via otp , 2factor authentication 