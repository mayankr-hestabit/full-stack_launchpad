import mongoose from "mongoose";
import bcrypt from "bcrypt";

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, "Name is required"],
    trim: true,
    maxlength: 50,
  },

  email: {
    type: String,
    required: [true, "Email is required"],
    unique: true,
    lowercase: true,
    trim: true,
  },

  password: {
    type: String,
    required: [true, "Password is required"],
    minlength: 8,
  },

  age: {
    type: Number,
    min: 18,
  },

  isActive: {
    type: Boolean,
    default: true,
  },
},
{
  timestamps: true,
}
);

userSchema.pre("save", async function () {
    this.password = await bcrypt.hash(this.password, 10);
});

const User = mongoose.model("User", userSchema);

export default User;